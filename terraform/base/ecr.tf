# A implementar primeiro: repositórios das imagens de indexing e retrieval.

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

output "indexing_repository_url" {
  value = aws_ecr_repository.indexing.repository_url
}

output "retrieval_repository_url" {
  value = aws_ecr_repository.retrieval.repository_url
}