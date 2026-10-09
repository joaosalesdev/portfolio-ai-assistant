resource "aws_lambda_permission" "s3_indexing" {
  statement_id   = "AllowDocumentsBucketInvoke"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.indexing.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = local.documents_bucket_arn
  source_account = data.aws_caller_identity.current.account_id
}

# Este recurso deve ser o único proprietário das notificações deste bucket.
resource "aws_s3_bucket_notification" "documents" {
  bucket = local.documents_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.indexing.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.documents_prefix
  }

  depends_on = [aws_lambda_permission.s3_indexing]
}
