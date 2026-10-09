variable "project_name" {
  description = "Nome usado como prefixo dos recursos."
  type        = string
  default     = "portfolio-ai-assistant"
}

variable "documents_prefix" {
  description = "Prefixo dos documentos aprovados que podem disparar indexing."
  type        = string
  default     = "documents/"

  validation {
    condition     = length(var.documents_prefix) > 0 && endswith(var.documents_prefix, "/")
    error_message = "Use um prefixo não vazio terminado em /, como documents/."
  }
}

variable "aws_region" {
  description = "Região AWS escolhida para os recursos."
  type        = string
  default     = "us-east-1"
}

variable "indexing_image_uri" {
  description = "URI da imagem de indexing com digest."
  type        = string
}

variable "retrieval_image_uri" {
  description = "URI da imagem de retrieval com digest."
  type        = string
}
