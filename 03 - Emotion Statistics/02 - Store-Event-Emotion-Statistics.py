import json
import boto3
import datetime

loggingTable = 'logs'
facesCollection = "Visitor-Faces" 
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Emotion-Statistics')
tableDL = dynamodb.Table('DeepLens')
s3 = boto3.client('s3') 

def lambda_handler(event, context):
    # Handle Multiple Records
    for eachRec in event['Records']:
        
        # Check Trigger Event On Modify
        if 'eventName' in eachRec and eachRec['eventName'] == "MODIFY":
            
            # Gurantee All Att. Exist
            if 'status' in eachRec['dynamodb']['NewImage']:
                if 'status' in eachRec['dynamodb']['OldImage']:
                    newEvent = eachRec['dynamodb']['NewImage']['status']['S']
                    oldEvent = eachRec['dynamodb']['OldImage']['status']['S']
                    
                    if oldEvent == "Running" and newEvent == "Stopped":
                        
                        # Declare Arrays For Loop Keys
                        emotions = ["SAD", "CALM", "ANGRY", "HAPPY", "CONFUSED", "FEAR", "DISGUSTED", "SURPRISED"]
                        statType = ["adultsEmotion", "childrenEmotion", "maleEmotion", "femaleEmotion", "totalEmotion"]
                        
                        eventID = (table.get_item(Key={'emotion': 'eventID'}))['Item']['eventID']
                        
                        totalEmotion =[]
                        maleEmotion = []
                        femaleEmotion = []
                        adultsEmotion = []
                        childrenEmotion =[]
                        
                        # Loop Through Emotion Statistics DynamoDB Column By Column
                        for eachStatType in statType:
                            for eachEmotion in emotions:
                                data = table.get_item(Key={'emotion': eachEmotion})
                                if data['Item'].get(eachStatType) is not None:
                                    data = int(data['Item'].get(eachStatType))
                                    if data is not None:
                                        if eachStatType == "adultsEmotion":
                                            adultsEmotion.append(data)
                                        elif eachStatType == "childrenEmotion":
                                            childrenEmotion.append(data)
                                        elif eachStatType == "maleEmotion":
                                            maleEmotion.append(data)
                                        elif eachStatType == "femaleEmotion":
                                            femaleEmotion.append(data)
                                        elif eachStatType == "totalEmotion":
                                            totalEmotion.append(data)
                                            
                                            
                        # Convert Statistics to JSON            
                        data = {} 
                        data['emotion'] = []
                        data['emotion'].append({
                            'eventID' : eventID,
                            'totalEmotions' : totalEmotion,
                            'femaleEmotions' : femaleEmotion,
                            'maleEmotions' : maleEmotion,
                            'adultsEmotions' : adultsEmotion,
                            'childrenEmotions' : childrenEmotion
                        })
                        
                        # Store the whole emotions captured during the EVENT
                        bucket_to='zayirna'
                        key_name = 'visitorEmotions/' + eventID + '.json'
                        result = s3.put_object(Body=json.dumps(data), Bucket=bucket_to, Key=key_name)
                        
                        # Clear DeepLens Table
                        deepLensList = tableDL.scan()
                        for eachItem in deepLensList['Items']:
                            response = tableDL.delete_item(
                                Key={
                                    'deepLensName': eachItem['deepLensName']
                                }
                            )
                        
                        # Clear Emotion Statistics Table
                        with table.batch_writer() as batch:
                            for emotion in emotions:
                                batch.put_item(
                                    Item={
                                         "adultsEmotion": 0,
                                         "childrenEmotion": 0,
                                          "emotion": emotion,
                                          "femaleEmotion": 0,
                                          "maleEmotion": 0,
                                          "totalEmotion": 0
                                    }
                                )
                        print('Tables are been Cleared')
                        
                        # try:
                        #     rekognition.delete_collection(CollectionId=facesCollection)
                        # except:
                        #     rekognition.create_collection(CollectionId=facesCollection)
                        #     rekognition.delete_collection(CollectionId=facesCollection)