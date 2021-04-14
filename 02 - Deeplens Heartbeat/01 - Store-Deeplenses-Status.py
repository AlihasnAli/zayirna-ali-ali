import json
import boto3
import uuid
import datetime

# dynamodb = boto3.client('dynamodb')
deeplenTable = 'DeepLens'
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    
    # Handle Multiple Records
    for eachRec in event['Records']:
        
        # Check Trigger Event On Insert 
        if eachRec['eventName'] == "INSERT":
            
            # Gurantee All Att. Exist
            if 'deeplensName' in eachRec['dynamodb']['NewImage']:
                dlName = eachRec['dynamodb']['NewImage']['deeplensName']['S']
                dlLastPT = eachRec['dynamodb']['NewImage']['occurranceTime']['S']
                print(dlName)
                print(dlLastPT)
                
                # Fetch & Update Available Heartbeat Into Deeplens DynamoDB
                dynamodb.put_item(
                    TableName=deeplenTable,
                    Item={
                        'deepLensName': {'S':dlName},
                        'lastHeartBeat': {'S':dlLastPT} 
                    })
            
            
