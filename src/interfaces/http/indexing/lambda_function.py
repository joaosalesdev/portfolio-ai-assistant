# LAMBDA INDEXING.

def lambda_handler(event, context):
    print("Lambda Indexing")
    
    print("EVENT: ")
    print(event)
    
    print("CONTEXT: ")
    print(context)

    return {
        "statusCode": 200,
        "body": "Lambda Indexing executed!"
    }