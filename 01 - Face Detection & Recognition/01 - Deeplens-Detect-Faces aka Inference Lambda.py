import json
import awscam
import mo
import cv2
import greengrasssdk
import os
import boto3
import uuid
import datetime
import time
from botocore.session import Session

dataTable = 'Faces'                                     # The name of the DynamoDB table that stores visitors' attributes
eventTable = 'ScheduledEvents'                          # Table to get running event ID
loggingTable = 'logs'                                   # The name of the DynamoDB table that stores log files
deepLensName = 'dep1'                                   # Deeplens Name
facesCollection = "Visitor-Faces"                       # Name of the face collection that the AWS Rekognition use to store facial features
faceMatchThreshold = 70                                 # The threshold of similarity considering same person face detection

session = Session()                                     # Create a session for AWS Services
s3 = session.create_client('s3')                        # Create S3 Bucket Session
dynamodb = session.create_client('dynamodb')            # Create DynamoDB Session
dynamodbeResource = boto3.resource('dynamodb')          # Create DynamoDB Resource Object
rekognition = session.create_client('rekognition')      # Create AWS Rekognition Session


def function_handler(event, context):
    """Empty entry point to the Lambda function invoked from the edge."""
    return

def infinite_infer_run(eventID, endTime):
    """ Run the DeepLens inference loop frame by frame"""
    
    # Model Info
    model_type = 'ssd'
    model_path = '/opt/awscam/artifacts/mxnet_deploy_ssd_FP16_FUSED.xml'
    model = awscam.Model(model_path, {'GPU': 1})
    
    # Face & Image Specs
    detection_threshold = 0.5
    input_height = 300
    input_width = 300
    
    # Sync time with Bahrain add 8 hours
    while endTime > datetime.datetime.now() + datetime.timedelta(hours=8):
        try:
            # Get a frame from the video stream
            ret, frame = awscam.getLastFrame()
            
            if not ret:
                raise Exception('Failed to get frame from the stream')
                
            frame_resize = cv2.resize(frame, (input_height, input_width))
            parsed_inference_results = model.parseResult(model_type, model.doInference(frame_resize))
            yscale = float(frame.shape[0]) / float(input_height)
            xscale = float(frame.shape[1]) / float(input_width)
            
            # Get highest propabilities 
            getHighProp = 4
            for obj in parsed_inference_results[model_type][0:getHighProp]:
                if obj['prob'] > detection_threshold:
                    xminF = int( xscale * obj['xmin'] ) + int((obj['xmin'] - input_width/2) + input_width/2)
                    yminF = int( yscale * obj['ymin'] )
                    xmaxF = int( xscale * obj['xmax'] ) + int((obj['xmax'] - input_width/2) + input_width/2)
                    ymaxF = int( yscale * obj['ymax'] )
                    faceImage = frame[yminF:ymaxF, xminF:xmaxF]
                    
                    _, jpg_data = cv2.imencode('.jpg', faceImage)
                    image = {'Bytes': jpg_data.tostring()}
                    faces = rekognition.search_faces_by_image(
                        FaceMatchThreshold=faceMatchThreshold,
                        CollectionId=facesCollection,
                        Image=image,
                        MaxFaces=1
                    )
                    
                    eventID = eventID.replace('-','')
                    facesIndex = None
                    key = None
                    
                    # Visitor face is already registered in the collection
                    if len(faces['FaceMatches']) == 1:
                        # Recognise visitor again and set isRedundant value to true
                        isRedundant = 'true'
                        facesIndex = rekognition.index_faces(
                        Image=image,
                        CollectionId=facesCollection,
                        DetectionAttributes=['ALL'])
                        key = 're-face-' + str(eventID)+ '-' + deepLensName + '-' + str(uuid.uuid1()) + '-' + str(uuid.uuid4()) +'.json' 
                    # Visitor face is NOT registered in the collection
                    else:
                        # Recognise visitor and set isRedundant value to false
                        isRedundant = 'false'
                        facesIndex = rekognition.index_faces(
                        Image=image,
                        CollectionId=facesCollection,
                        DetectionAttributes=['ALL'])
                        key = 'uq-face-' + str(eventID) + '-' + deepLensName + '-'  + str(uuid.uuid1()) + '-' + str(uuid.uuid4())  +'.json'
                        
                    bucket_name='visitor-faces-bucket-fr'
                    result = s3.put_object(Body=json.dumps(facesIndex), Bucket=bucket_name, Key=key)
        except:
            print('There is an error in the While Loop')    


def CheckForRunningEvent():
    table = dynamodbeResource.Table(eventTable)
    resp = table.scan()
    items = resp['Items']    
    for eachItem in items:
        if eachItem.get('status') == 'Running':
            eventID = eachItem['eventID']
            if eventID is not None:
                timeNow = datetime.datetime.now() + datetime.timedelta(hours=8)
                dateToday = datetime.datetime.strftime(timeNow, '%Y-%m-%d')
                
                endTimeStr = eachItem['endTime']
                endTimeStr += '.000001'
                endTimeStr = endTimeStr[10:]
                
                endTime = dateToday + endTimeStr
                endTime = datetime.datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S.%f')
                
                infinite_infer_run(eventID, endTime)
                    
    # Re-run this ever one second
    Timer(1,CheckForRunningEvent).start()
    
CheckForRunningEvent()