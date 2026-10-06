variable "project_name" {
  description = "Nome usado como prefixo dos recursos."
  type        = string
  default     = "portfolio-ai-assistant"
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
