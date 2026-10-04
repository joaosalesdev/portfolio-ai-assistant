# LAMBDA INDEXING.

def lambda_handler(event, context):
    print("Lambda Indexing")

    return {
        "statusCode": 200,
        "body": "Lambda executed!"
    }