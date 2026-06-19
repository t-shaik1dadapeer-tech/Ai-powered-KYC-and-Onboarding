variable "project_name" {
  type        = string
  description = "Project identifier"
  default     = "kyc-platform"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "dev"
}

variable "services" {
  type        = list(string)
  description = "Managed service names"
  default     = ["onboarding-api", "postgres", "prometheus", "grafana"]
}
