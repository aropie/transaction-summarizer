output "rds_hostname" {
  description = "RDS instance hostname"
  value       = aws_db_instance.transactions-db.address
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.transactions-db.port
  sensitive   = true
}

output "rds_username" {
  description = "RDS instance root username"
  value       = aws_db_instance.transactions-db.username
  sensitive   = true
}

output "api_url" {
  description = "URL to invoke the API"
  value       = aws_api_gateway_stage.prod.invoke_url
}
