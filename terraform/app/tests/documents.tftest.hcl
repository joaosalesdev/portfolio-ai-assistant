mock_provider "aws" {
  mock_data "aws_caller_identity" {
    defaults = { account_id = "123456789012" }
  }
  mock_data "aws_partition" {
    defaults = { partition = "aws" }
  }
}

variables {
  openai_api_key = "test-key-not-real"
  database_url   = "postgresql://test:test@localhost/test"
  indexing_image_uri  = "123456789012.dkr.ecr.us-east-1.amazonaws.com/indexing@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  retrieval_image_uri = "123456789012.dkr.ecr.us-east-1.amazonaws.com/retrieval@sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
}

run "documents_event_access" {
  command = plan

  assert {
    condition     = aws_s3_bucket_notification.documents.bucket == "portfolio-ai-assistant-documents-123456789012-us-east-1"
    error_message = "App deve usar o nome do bucket criado por base."
  }

  assert {
    condition     = one(aws_s3_bucket_notification.documents.lambda_function).filter_prefix == "documents/" && contains(one(aws_s3_bucket_notification.documents.lambda_function).events, "s3:ObjectCreated:*")
    error_message = "Apenas uploads no prefixo aprovado devem disparar indexing."
  }

  assert {
    condition     = aws_lambda_permission.s3_indexing.source_account == "123456789012" && aws_lambda_permission.s3_indexing.source_arn == local.documents_bucket_arn
    error_message = "A permissão de invocação deve estar limitada ao bucket e à conta."
  }

  assert {
    condition     = jsondecode(aws_iam_role_policy.indexing_documents.policy).Statement[0].Resource == "${local.documents_bucket_arn}/documents/*"
    error_message = "A Lambda deve ler apenas o prefixo aprovado."
  }
}

run "custom_prefix" {
  command = plan
  variables {
    documents_prefix = "approved/"
  }
  assert {
    condition     = one(aws_s3_bucket_notification.documents.lambda_function).filter_prefix == "approved/" && jsondecode(aws_iam_role_policy.indexing_documents.policy).Statement[0].Resource == "${local.documents_bucket_arn}/approved/*"
    error_message = "O filtro e a permissão de leitura devem acompanhar o prefixo configurado."
  }
}

run "reject_empty_prefix" {
  command = plan
  variables {
    documents_prefix = ""
  }
  expect_failures = [var.documents_prefix]
}

run "lambda_environment" {
  command = plan

  assert {
    condition = alltrue([
      for function in [aws_lambda_function.indexing, aws_lambda_function.retrieval] :
      function.environment[0].variables == tomap({
        OPENAI_API_KEY = var.openai_api_key
        DATABASE_URL   = var.database_url
      })
    ])
    error_message = "Both Lambdas must receive only the two application environment variables."
  }
}

run "reject_empty_api_key" {
  command = plan
  variables {
    openai_api_key = ""
  }
  expect_failures = [var.openai_api_key]
}

run "reject_empty_database_url" {
  command = plan
  variables {
    database_url = ""
  }
  expect_failures = [var.database_url]
}

run "retrieval_public_url_and_cors" {
  command = plan

  assert {
    condition     = aws_lambda_function_url.retrieval.function_name == aws_lambda_function.retrieval.function_name && aws_lambda_function_url.retrieval.authorization_type == "NONE"
    error_message = "Only retrieval should expose the public chat URL."
  }

  assert {
    condition     = one(aws_lambda_function_url.retrieval.cors).allow_origins == toset(["https://joaosalesdev.github.io"]) && one(aws_lambda_function_url.retrieval.cors).allow_methods == toset(["POST"]) && one(aws_lambda_function_url.retrieval.cors).allow_headers == toset(["content-type"])
    error_message = "CORS must allow only the portfolio origin, POST and content-type."
  }

}
