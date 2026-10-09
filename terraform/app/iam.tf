# A implementar: roles separadas e permissões mínimas para cada Lambda.

resource "aws_iam_role_policy" "indexing_documents" {
  name = "read-approved-documents"
  role = aws_iam_role.indexing_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:GetObjectVersion"]
      Resource = "${local.documents_bucket_arn}/${var.documents_prefix}*"
    }]
  })
}

resource "aws_iam_role" "indexing_lambda" {
  name = "portfolio-ai-assistant-indexing"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role" "retrieval_lambda" {
  name = "portfolio-ai-assistant-retrieval"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}
