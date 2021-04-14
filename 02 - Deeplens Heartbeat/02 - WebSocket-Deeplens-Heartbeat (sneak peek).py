#ensure that an update is what triggered the function, and the updated record is one of the aggregate values
        if record['eventName'] == "MODIFY" and "aggregateValue" in record["dynamodb"]["NewImage"]:
            
            #get the updated aggregates by querying the table to get all data with partition key "AGGREGATES"
            response = table.query(KeyConditionExpression=Key('partitionKey').eq('AGGREGATES'))
            
            #converting query result to json and save it into an array
            aggregatesJSON = []
            for i in response['Items']:
                d = ast.literal_eval(json.dumps(i, cls=DecimalEncoder))
                aggregatesJSON.append(d)
        
            # Get Data From Deeplens DynamoDB
            tableDeepLens = dynamodb.Table(deeplensTable)
            resp = tableDeepLens.scan()
            deepLenses = resp['Items']    
            for eachDeepLens in deepLenses:
                aggregatesJSON.append(eachDeepLens)