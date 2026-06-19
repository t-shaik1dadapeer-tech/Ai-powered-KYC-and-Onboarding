output "infra_registry_path" {
  value       = local_file.infra_registry.filename
  description = "Path to generated infrastructure registry JSON"
}

output "compose_checksum" {
  value       = sha256(file("${path.module}/../docker/docker-compose.yml"))
  description = "SHA256 of docker-compose.yml for drift detection"
}

output "environment" {
  value = var.environment
}
