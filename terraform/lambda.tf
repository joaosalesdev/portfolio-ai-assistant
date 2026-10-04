# A implementar: duas Lambdas com imagens já publicadas no ECR.
# Indexing administrativa, sem URL pública; retrieval com Function URL.


# Package Indexing Lambda
data "archive_file" "indexing" {
  type        = "zip"
  source_dir  = "${path.module}/../src/interfaces/http/indexing"
  output_path = "${path.module}/.build/indexing.zip"
}

# Indexing Lambda
resource "aws_lambda_function" "indexing" {
  function_name = "portfolio-ai-assistant-indexing"

  filename         = data.archive_file.indexing.output_path
  source_code_hash = data.archive_file.indexing.output_base64sha256

  handler = "lambda_function.lambda_handler"
  runtime = "python3.14"

  role = aws_iam_role.indexing_lambda.arn
}



# Package Retrieval Lambda
data "archive_file" "retrieval" {
  type        = "zip"
  source_dir  = "${path.module}/../src/interfaces/http/retrieval"
  output_path = "${path.module}/.build/retrieval.zip"
}

# Retrieval Lambda
resource "aws_lambda_function" "retrieval" {
  function_name = "portfolio-ai-assistant-retrieval"

  filename         = data.archive_file.retrieval.output_path
  source_code_hash = data.archive_file.retrieval.output_base64sha256

  handler = "lambda_function.lambda_handler"
  runtime = "python3.14"

  role = aws_iam_role.retrieval_lambda.arn
}

