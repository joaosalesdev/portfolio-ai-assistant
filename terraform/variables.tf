variable "project_name" {
  description = "Nome usado como prefixo dos recursos."
  type        = string
  default     = "portfolio-ai-assistant"
}

variable "aws_region" {
  description = "Região AWS escolhida para os recursos."
  type        = string
}
