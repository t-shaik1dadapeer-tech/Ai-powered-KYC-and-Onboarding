terraform {
  required_version = ">= 1.5.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

provider "local" {}

resource "local_file" "infra_registry" {
  filename = "${path.module}/.generated/infra-registry.json"
  content = jsonencode({
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
    artifacts = {
      docker_compose = sha256(file("${path.module}/../docker/docker-compose.yml"))
      k8s_deployment = sha256(file("${path.module}/../kubernetes/onboarding-api-deployment.yaml"))
      prometheus     = sha256(file("${path.module}/../prometheus/prometheus.yml"))
    }
    services = var.services
    generated_at   = timestamp()
  })
}

resource "local_file" "compose_copy" {
  filename = "${path.module}/.generated/docker-compose.resolved.yml"
  content  = file("${path.module}/../docker/docker-compose.yml")
}
