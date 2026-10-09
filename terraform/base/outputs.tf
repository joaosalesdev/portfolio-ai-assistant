output "documents_bucket_name" {
  description = "Bucket privado para upload dos documentos aprovados."
  value       = aws_s3_bucket.documents.id
}

output "documents_bucket_arn" {
  description = "ARN do bucket de documentos."
  value       = aws_s3_bucket.documents.arn
}
