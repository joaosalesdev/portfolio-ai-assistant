# Repositórios das imagens de indexing e retrieval.

resource "aws_ecr_repository" "indexing" {
  name                 = "${var.project_name}-indexing"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "retrieval" {
  name                 = "${var.project_name}-retrieval"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Retém as três imagens mais recentes por data de push, com ou sem tags.
resource "aws_ecr_lifecycle_policy" "retain_latest" {
  for_each = {
    indexing  = aws_ecr_repository.indexing.name
    retrieval = aws_ecr_repository.retrieval.name
  }

  repository = each.value
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only the 3 most recently pushed images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 3
      }
      action = {
        type = "expire"
      }
    }]
  })
}

output "indexing_repository_url" {
  value = aws_ecr_repository.indexing.repository_url
}

output "retrieval_repository_url" {
  value = aws_ecr_repository.retrieval.repository_url
}
