.PHONY: test test-coverage test-e2e test-api test-intelligence test-node test-rust \
        docker-build docker-up docker-down docker-verify ci-local observability-verify \
        worktree-demo

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
EVIDENCE := $(ROOT)evidence/test-results

test: test-coverage

test-coverage:
	bash $(ROOT)scripts/run-all-tests.sh

test-e2e:
	cd $(ROOT)services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -v $(ROOT)tests/e2e/

test-api:
	cd $(ROOT)services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -v --cov=app --cov-report=term-missing

test-intelligence:
	cd $(ROOT)engines/intelligence && PYTHONPATH=src .venv/bin/pytest -v

test-node:
	cd $(ROOT)clients/node-cli && npm test

test-rust:
	cd $(ROOT)engines/rust-analyzer && cargo test

docker-build:
	cd $(ROOT)infra/docker && docker compose build

docker-up:
	cd $(ROOT)infra/docker && docker compose up -d

docker-down:
	cd $(ROOT)infra/docker && docker compose --profile tools down

docker-verify:
	bash $(ROOT)scripts/docker-verify.sh

ci-local:
	bash $(ROOT)scripts/ci-local.sh

observability-verify:
	bash $(ROOT)scripts/observability-verify.sh

worktree-demo:
	bash $(ROOT)scripts/worktree-demo.sh
