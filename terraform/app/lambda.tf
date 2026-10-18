# Container-based Lambdas. Retrieval Function URL is not implemented yet.

# Indexing Lambda
resource "aws_lambda_function" "indexing" {
  function_name = local.indexing_function_name
  timeout       = 120
  role          = aws_iam_role.indexing_lambda.arn

  package_type  = "Image"
  image_uri     = var.indexing_image_uri
  architectures = ["x86_64"]

  environment {
    variables = {
      OPENAI_API_KEY = var.openai_api_key
      DATABASE_URL   = var.database_url
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.indexing,
    aws_iam_role_policy.indexing_logs,
    aws_iam_role_policy.indexing_documents
  ]
}



# Retrieval Lambda
resource "aws_lambda_function" "retrieval" {
  function_name = local.retrieval_function_name
  timeout       = 120
  role          = aws_iam_role.retrieval_lambda.arn

  package_type  = "Image"
  image_uri     = var.retrieval_image_uri
  architectures = ["x86_64"]

  environment {
    variables = {
      OPENAI_API_KEY = var.openai_api_key
      DATABASE_URL   = var.database_url
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.retrieval,
    aws_iam_role_policy.retrieval_logs
  ]
}
