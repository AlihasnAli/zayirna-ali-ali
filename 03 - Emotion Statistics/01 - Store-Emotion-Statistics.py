import json
import boto3
import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Emotion-Statistics')

dynamodbtest = boto3.client('dynamodb')
test_table = 'logs'

def lambda_handler(event, context):
    # Handle Multiple Records
    for eachRec in event['Records']:
        
        # Check Trigger Event On Insertion
        if eachRec['eventName'] == "INSERT": 
            
            # Gurantee All Att. Exist
            if 'gender' in eachRec.get('dynamodb').get('NewImage'):
                if 'emotion' in eachRec.get('dynamodb').get('NewImage'):
                    if 'age' in eachRec.get('dynamodb').get('NewImage'):
                        if 'ageGroup' in eachRec.get('dynamodb').get('NewImage'):
                            eventID = eachRec.get('dynamodb').get('NewImage').get('partitionKey').get('S')
                            visitorGender = eachRec.get('dynamodb').get('NewImage').get('gender').get('S')
                          
                            meanAge = eachRec['dynamodb']['NewImage']['age']['S']
                            ageGroup = eachRec['dynamodb']['NewImage']['ageGroup']['S']
                            faceEmotion = eachRec['dynamodb']['NewImage']['emotion']['S'] 
                            
                            # Identify The Gender
                            if visitorGender == 'Male':
                                # Update Based On The Age Group
                                if ageGroup == 'Adult':
                                    table.update_item(
                                        Key={
                                            'emotion': str(faceEmotion)
                                        },
                                        UpdateExpression='ADD adultsEmotion :a, maleEmotion :m, totalEmotion :t',
                                        ExpressionAttributeValues={
                                            ':a': 1,
                                            ':m': 1,
                                            ':t': 1
                                        }
                                    ),
                                elif ageGroup == 'Child':
                                    table.update_item(
                                        Key={
                                            'emotion': str(faceEmotion)
                                        },
                                        UpdateExpression='ADD childrenEmotion :c, maleEmotion :m, totalEmotion :t',
                                        ExpressionAttributeValues={
                                            ':c': 1,
                                            ':m': 1,
                                            ':t': 1
                                        }
                                    ),
                                    
                            # Identify The Gender 
                            elif visitorGender == 'Female':
                                # Update Based On The Age Group
                                if ageGroup == 'Adult':
                                    table.update_item(
                                        Key={
                                            'emotion': str(faceEmotion)
                                        },
                                        UpdateExpression='ADD adultsEmotion :a, femaleEmotion :f, totalEmotion :t',
                                        ExpressionAttributeValues={
                                            ':a': 1,
                                            ':f': 1,
                                            ':t': 1
                                        }
                                    ),
                                elif ageGroup == 'Child':
                                    table.update_item(
                                        Key={
                                            'emotion': str(faceEmotion)
                                        },
                                        UpdateExpression='ADD childrenEmotion :c, femaleEmotion :f, totalEmotion :t',
                                        ExpressionAttributeValues={
                                            ':c': 1,
                                            ':f': 1,
                                            ':t': 1
                                        }
                                    ),
                                    
                            table.put_item(
                              Item={
                                    'emotion': 'eventID',
                                    'eventID': eventID
                                }
                            )
                            
                           
            
            
            
    
    

    
    
    
            