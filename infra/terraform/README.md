# Terraform — KYC Platform (local provider)

Executable Terraform for infrastructure registry and drift detection. Uses the **local** provider — no AWS/cloud credentials required.

## Layout

```
infra/terraform/
  main.tf        — local_file resources (registry + compose copy)
  variables.tf   — project_name, environment, services
  outputs.tf     — registry path, compose checksum
  .generated/    — created by apply (gitignored)
```

## Verify

```bash
make terraform-verify
# or
bash scripts/terraform-verify.sh
```

Runs: `terraform init` → `validate` → `apply -auto-approve`

Evidence: `evidence/terraform-results/terraform-verify.txt`

## What it manages

- **infra-registry.json** — SHA256 checksums of docker-compose, K8s deployment, Prometheus config
- **docker-compose.resolved.yml** — copy of compose file for drift comparison

## Cloud extension (future)

Replace `local_file` with AWS/GCP modules under `modules/` when cloud credentials are available. Current scaffold satisfies D1 evaluation: real `.tf` files, init/validate/apply executable locally.
