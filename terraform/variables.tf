variable "aws_region" {
  description = "The region where the infrastructure should be deployed to"
  type        = string
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "provision_db" {
  description = "Whether to provision a PostgreSQL RDS instance"
  type        = bool
  default     = true
}

variable "db_password" {
  description = "RDS root user password"
  type        = string
  sensitive   = true
}
