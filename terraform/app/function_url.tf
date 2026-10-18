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

resource "aws_lambda_permission" "retrieval_url" {
  statement_id           = "AllowPublicFunctionUrl"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.retrieval.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "retrieval_url_invoke" {
  statement_id             = "AllowPublicInvokeViaFunctionUrl"
  action                   = "lambda:InvokeFunction"
  function_name            = aws_lambda_function.retrieval.function_name
  principal                = "*"
  invoked_via_function_url = true
}
