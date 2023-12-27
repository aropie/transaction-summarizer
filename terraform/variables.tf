variable "aws_region" {
  description = "The region where the infrastructure should be deployed to"
  type        = string
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "db_password" {
  description = "RDS root user password"
  type        = string
  sensitive   = true
}
