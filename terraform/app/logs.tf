resource "aws_cloudwatch_log_group" "indexing" {
  name              = "/aws/lambda/${local.indexing_function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "retrieval" {
  name              = "/aws/lambda/${local.retrieval_function_name}"
  retention_in_days = 30
}

resource "aws_iam_role_policy" "indexing_logs" {
  name = "cloudwatch-logs"
  role = aws_iam_role.indexing_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.indexing.arn}:*"
    }]
  })
}

resource "aws_iam_role_policy" "retrieval_logs" {
  name = "cloudwatch-logs"
  role = aws_iam_role.retrieval_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.retrieval.arn}:*"
    }]
  })
}
