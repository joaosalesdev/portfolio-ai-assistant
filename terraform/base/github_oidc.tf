# O provider OIDC é compartilhado pela conta AWS: criar apenas uma vez.
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-github-actions"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = data.aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = "repo:joaosalesdev/portfolio-ai-assistant:ref:refs/heads/main"
        }
      }
    }]
  })
}

# Nesta etapa, a role publica imagens. Permissões de deploy serão adicionadas
# quando os recursos da aplicação e o acesso ao seu estado estiverem definidos.
resource "aws_iam_role_policy" "github_actions_ecr" {
  name = "ecr-publish"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "EcrLogin"
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Sid    = "PublishProjectImages"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:DescribeImages"
        ]
        Resource = [
          aws_ecr_repository.indexing.arn,
          aws_ecr_repository.retrieval.arn
        ]
      }
    ]
  })
}

output "github_actions_role_arn" {
  description = "Role que o workflow da branch main assume via OIDC."
  value       = aws_iam_role.github_actions.arn
}
