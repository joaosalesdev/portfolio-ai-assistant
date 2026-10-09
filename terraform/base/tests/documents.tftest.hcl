mock_provider "aws" {
  mock_data "aws_caller_identity" {
    defaults = { account_id = "123456789012" }
  }
  mock_data "aws_partition" {
    defaults = { partition = "aws" }
  }
}

run "private_versioned_documents" {
  command = plan

  assert {
    condition     = aws_s3_bucket.documents.bucket == "portfolio-ai-assistant-documents-123456789012-us-east-1" && !aws_s3_bucket.documents.force_destroy
    error_message = "O bucket deve ter nome compatível com app e preservar objetos na destruição."
  }
  assert {
    condition     = aws_s3_bucket_public_access_block.documents.block_public_acls && aws_s3_bucket_public_access_block.documents.block_public_policy && aws_s3_bucket_public_access_block.documents.ignore_public_acls && aws_s3_bucket_public_access_block.documents.restrict_public_buckets
    error_message = "Todas as proteções de acesso público devem estar habilitadas."
  }
  assert {
    condition     = one(aws_s3_bucket_versioning.documents.versioning_configuration).status == "Enabled"
    error_message = "O bucket deve preservar versões dos documentos."
  }
  assert {
    condition     = one(aws_s3_bucket_ownership_controls.documents.rule).object_ownership == "BucketOwnerEnforced"
    error_message = "ACLs devem estar desabilitadas."
  }
}
