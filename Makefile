.PHONY: test test-coverage test-e2e test-api test-intelligence test-node test-rust \
        docker-build docker-up docker-down docker-verify ci-local observability-verify \
        worktree-demo verify-phases evidence-index final-review export-openapi \
        terraform-verify k8s-verify load-test safe-change-check grafana-import-dashboard \
        full-24-audit bootstrap setup-github push push-first

ROOT := $(CURDIR)/
EVIDENCE := $(ROOT)evidence/test-results

test: test-coverage

test-coverage:
	bash "$(ROOT)scripts/run-all-tests.sh"

test-e2e:
	cd "$(ROOT)services/onboarding-api" && PYTHONPATH=. .venv/bin/pytest -v "$(ROOT)tests/e2e/"

test-api:
	cd "$(ROOT)services/onboarding-api" && PYTHONPATH=. .venv/bin/pytest -v --cov=app --cov-report=term-missing

test-intelligence:
	cd "$(ROOT)engines/intelligence" && PYTHONPATH=src .venv/bin/pytest -v

test-node:
	cd "$(ROOT)clients/node-cli" && npm test

test-rust:
	cd "$(ROOT)engines/rust-analyzer" && cargo test

docker-build:
	cd "$(ROOT)infra/docker" && docker compose build

docker-up:
	cd "$(ROOT)infra/docker" && docker compose up -d

docker-down:
	cd "$(ROOT)infra/docker" && docker compose --profile tools --profile bundled-grafana down

docker-verify:
	bash "$(ROOT)scripts/docker-verify.sh"

ci-local:
	bash "$(ROOT)scripts/ci-local.sh"

observability-verify:
	bash "$(ROOT)scripts/observability-verify.sh"

worktree-demo:
	bash "$(ROOT)scripts/worktree-demo.sh"

verify-phases:
	bash "$(ROOT)scripts/verify-all-phases.sh"

evidence-index:
	bash "$(ROOT)scripts/evidence-index.sh"

final-review:
	bash "$(ROOT)scripts/final-review.sh"

export-openapi:
	bash "$(ROOT)scripts/export-openapi.sh"

terraform-verify:
	bash "$(ROOT)scripts/terraform-verify.sh"

k8s-verify:
	bash "$(ROOT)scripts/k8s-verify.sh"

load-test:
	bash "$(ROOT)scripts/load-test.sh"

safe-change-check:
	bash "$(ROOT)scripts/safe-change-check.sh"

grafana-import-dashboard:
	bash "$(ROOT)scripts/grafana-import-dashboard.sh"

full-24-audit:
	bash "$(ROOT)scripts/full-24-audit.sh"

bootstrap:
	bash "$(ROOT)scripts/bootstrap.sh"

setup-github:
	bash "$(ROOT)scripts/setup-github-auth.sh"

push:
	bash "$(ROOT)scripts/git-push.sh"

push-first:
	bash "$(ROOT)scripts/git-push.sh" main
