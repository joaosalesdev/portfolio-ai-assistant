data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

# O bucket pertence ao estado base; app gerencia somente sua notificação.
# O nome determinístico evita conceder acesso ao estado completo de base.
locals {
  documents_bucket_name = "${var.project_name}-documents-${data.aws_caller_identity.current.account_id}-${var.aws_region}"
  documents_bucket_arn  = "arn:${data.aws_partition.current.partition}:s3:::${local.documents_bucket_name}"
}
