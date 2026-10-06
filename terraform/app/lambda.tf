# A implementar: duas Lambdas com imagens já publicadas no ECR.
# Indexing administrativa, sem URL pública; retrieval com Function URL.

# Indexing Lambda
resource "aws_lambda_function" "indexing" {
  function_name = local.indexing_function_name
  role          = aws_iam_role.indexing_lambda.arn

  package_type  = "Image"
  image_uri     = var.indexing_image_uri
  architectures = ["x86_64"]

  depends_on = [
    aws_cloudwatch_log_group.indexing,
    aws_iam_role_policy.indexing_logs
  ]
}



# Retrieval Lambda
resource "aws_lambda_function" "retrieval" {
  function_name = local.retrieval_function_name
  role          = aws_iam_role.retrieval_lambda.arn

  package_type  = "Image"
  image_uri     = var.retrieval_image_uri
  architectures = ["x86_64"]

  depends_on = [
    aws_cloudwatch_log_group.retrieval,
    aws_iam_role_policy.retrieval_logs
  ]
}
