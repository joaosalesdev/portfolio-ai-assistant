# github_deploy.tf
data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

locals {
  app_function_names = ["${var.project_name}-indexing", "${var.project_name}-retrieval"]
  app_role_arns = [
    for name in local.app_function_names :
    "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:role/${name}"
  ]
  app_lambda_arns = [
    for name in local.app_function_names :
    "arn:${data.aws_partition.current.partition}:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${name}"
  ]
  app_log_arns = [
    for name in local.app_function_names :
    "arn:${data.aws_partition.current.partition}:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${name}:*"
  ]
  app_state_arn = "arn:${data.aws_partition.current.partition}:s3:::joaosalesdev-terraform-state/portfolio-ai-assistant/dev/app/terraform.tfstate"
}

# Permissões limitadas aos recursos atuais de app; ampliar conforme o RAG evoluir.
resource "aws_iam_role_policy" "github_actions_deploy" {
  name = "terraform-app-deploy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AppStateBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:${data.aws_partition.current.partition}:s3:::joaosalesdev-terraform-state"
        Condition = {
          StringLike = {
            "s3:prefix" = ["portfolio-ai-assistant/dev/app/*"]
          }
        }
      },
      {
        Sid      = "AppState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = local.app_state_arn
      },
      {
        Sid      = "AppStateLock"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "${local.app_state_arn}.tflock"
      },
      {
        Sid    = "AppLambdas"
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction", "lambda:GetFunction",
          "lambda:GetFunctionConfiguration", "lambda:GetFunctionCodeSigningConfig",
          "lambda:UpdateFunctionCode", "lambda:UpdateFunctionConfiguration",
          "lambda:DeleteFunction", "lambda:ListTags",
          "lambda:TagResource", "lambda:UntagResource", "lambda:ListVersionsByFunction"
        ]
        Resource = local.app_lambda_arns
      },
      {
        Sid    = "AppExecutionRoles"
        Effect = "Allow"
        Action = [
          "iam:CreateRole", "iam:GetRole", "iam:DeleteRole",
          "iam:UpdateAssumeRolePolicy", "iam:UpdateRoleDescription",
          "iam:TagRole", "iam:UntagRole", "iam:ListRoleTags",
          "iam:PutRolePolicy", "iam:GetRolePolicy", "iam:DeleteRolePolicy",
          "iam:ListRolePolicies", "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole"
        ]
        Resource = local.app_role_arns
      },
      {
        Sid      = "PassOnlyAppRolesToLambda"
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = local.app_role_arns
        Condition = {
          StringEquals = { "iam:PassedToService" = "lambda.amazonaws.com" }
        }
      },
      {
        Sid    = "AppLogGroups"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup", "logs:DeleteLogGroup",
          "logs:PutRetentionPolicy", "logs:DeleteRetentionPolicy",
          "logs:ListTagsForResource", "logs:TagResource", "logs:UntagResource"
        ]
        Resource = concat(local.app_log_arns, [
          for arn in local.app_log_arns : trimsuffix(arn, ":*")
        ])
      },
      {
        Sid      = "DescribeLogGroups"
        Effect   = "Allow"
        Action   = "logs:DescribeLogGroups"
        Resource = "*"
      }
    ]
  })
}

# A base gerencia a permissão de leitura da Lambda, evitando alterações
# automáticas da política do ECR durante o deploy da aplicação.
resource "aws_ecr_repository_policy" "lambda" {
  for_each = {
    indexing  = aws_ecr_repository.indexing.name
    retrieval = aws_ecr_repository.retrieval.name
  }
  repository = each.value
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "LambdaImageRead"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
      Condition = {
        ArnLike = { "aws:SourceArn" = local.app_lambda_arns }
      }
    }]
  })
}
