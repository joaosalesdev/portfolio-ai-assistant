# AWS provider 6.67.0 adds both public invocation permissions for auth NONE.
# Do not manage additional permission resources in parallel with URL creation.
resource "aws_lambda_function_url" "retrieval" {
  function_name      = aws_lambda_function.retrieval.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["https://joaosalesdev.github.io"]
    allow_methods = ["POST"]
    allow_headers = ["content-type"]
    max_age       = 300
  }
}
