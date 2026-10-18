output "retrieval_function_url" {
  description = "Public HTTPS endpoint for portfolio chat POST requests."
  value       = aws_lambda_function_url.retrieval.function_url
}
