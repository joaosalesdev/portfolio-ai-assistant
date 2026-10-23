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

variable "openai_api_key" {
  description = "OpenAI API key supplied externally; never commit the value."
  type        = string
  sensitive   = true

  validation {
    condition     = length(trimspace(var.openai_api_key)) > 0
    error_message = "openai_api_key must not be empty."
  }
}

variable "database_url" {
  description = "PostgreSQL connection URL supplied externally; never commit the value."
  type        = string
  sensitive   = true

  validation {
    condition     = length(trimspace(var.database_url)) > 0
    error_message = "database_url must not be empty."
  }
}

variable "telegram_bot_token" {
  description = "Optional Melita bot token; configure together with telegram_chat_id."
  type        = string
  sensitive   = true
  default     = ""

  validation {
    condition     = (length(trimspace(var.telegram_bot_token)) > 0) == (length(trimspace(var.telegram_chat_id)) > 0)
    error_message = "Configure both Telegram variables or leave both empty."
  }
}

variable "telegram_chat_id" {
  description = "Optional Telegram destination chat ID, supplied externally."
  type        = string
  sensitive   = true
  default     = ""
}
