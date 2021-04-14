import json
import uuid
import datetime
import os
import time
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
rekognition = boto3.client('rekognition')


dataTable = 'Events'  # The name of the DynamoDB table that stores visitors' attributes
loggingTable = 'logs'  # The name of the DynamoDB table that stores log files
faceMatchThreshold = 70  # The threshold of similarity considering same person face detection
facesCollection = 'Visitor-Faces'  # Name of the face collection that the AWS Rekognition use to store facial features


def lambda_handler(event, context):
    # Get Trigger Event Info
    eventRecord = event['Records'][0]['s3']
    bucket = eventRecord['bucket']['name']
    key = eventRecord['object']['key']

    # Get & Open S3 Object
    result = s3.get_object(Bucket=bucket, Key=key)
    faces_string = result["Body"].read().decode()

    # Retrieve Face Features
    faces = json.loads(faces_string)
    faceRecord = faces['FaceRecords'][0]
    faceRecordDetails = faceRecord['FaceDetail']
    isRedundant = None
    if key[:2] == 're':
        isRedundant = 'True'
    else:
        isRedundant = 'False'

    splitKey = key.split('-')
    eventID = splitKey[2]
    deeplens_name = splitKey[3]
    face_id = getVisitorFaceId(faceRecord)
    visitorGender = getVisitorGender(faceRecordDetails)
    low_age_range = getVisitorLowAge(faceRecordDetails)
    high_age_range = getVisitorHighAge(faceRecordDetails)
    meanAge = getVisitorAge(low_age_range, high_age_range)
    ageGroup = getVisitorAgeGroup(meanAge)
    faceEmotion = getVisitorEmotion(faceRecordDetails)
    
    # Fetch Face Record
    dynamodb.put_item(
        TableName=dataTable,
        Item={
            'partitionKey': {'S': str(eventID)},
            'metadata': {'S': 'fd-' + str(uuid.uuid4())},
            'faceID': {'S': face_id},
            'ageGroup': {'S': ageGroup},
            'gender': {'S': visitorGender},
            'isRedundant': {'S': str(isRedundant)},
            'emotion': {'S': str(faceEmotion)},
            # 'emotionConfidence': {'S': str(faceEmotionConfidence)},
            'age': {'S': str(int(meanAge))},
            # 'lowAge': {'S': str(low_age_range)},
            # 'highAge': {'S': str(high_age_range)},
            'occurranceTime': {'S': str(datetime.datetime.now() + datetime.timedelta(hours=3))},
            'deeplensName' : {'S': str(deeplens_name)}
        })

    message = ''
    if isRedundant == 'false':
        message = 'Congratulations! New Visitor have attended the event.'
    else:
        message = 'Redundant visitor is detected'
    dynamodb.put_item(
        TableName=loggingTable,
        Item={
            'occurrenceTime': {'S': str(datetime.datetime.now() +
                                        datetime.timedelta(hours=8))},
            'message': {'S': message}
        })


def getVisitorFaceId(faceRecord):
    faceID = faceRecord['Face']['FaceId']
    return faceID


def getVisitorGender(faceRecordDetails):
    gender = faceRecordDetails['Gender']['Value']
    return gender


def getVisitorLowAge(faceRecordDetails):
    lowAge = faceRecordDetails['AgeRange']['Low']
    return lowAge


def getVisitorHighAge(faceRecordDetails):
    lowAge = faceRecordDetails['AgeRange']['High']
    return lowAge


def getVisitorAge(low_age_range, high_age_range):
    meanAge = low_age_range + high_age_range
    meanAge = meanAge / 2
    return meanAge


def getVisitorAgeGroup(meanAge):
    ageGroup = ''
    if meanAge <= 16:
        ageGroup = 'Child'
    else:
        ageGroup = 'Adult'
    return ageGroup


def getVisitorEmotion(faceRecordDetails):
    faceEmotion = None
    faceEmotionConfidence = 0
    for emotion in faceRecordDetails['Emotions']:
        if emotion.get('Confidence') >= faceEmotionConfidence:
            faceEmotionConfidence = emotion['Confidence']
            faceEmotion = emotion.get('Type')
    return faceEmotion