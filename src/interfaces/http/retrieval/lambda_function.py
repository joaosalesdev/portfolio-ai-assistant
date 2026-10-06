# LAMBDA RETRIEVAL.

def lambda_handler(event, context):
    print("Lambda Retrieval")

    return {
        "statusCode": 200,
        "body": "Lambda Retrieval executed!"
    }