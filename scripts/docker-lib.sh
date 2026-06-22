#!/usr/bin/env bash
# Shared Docker helpers — daemon check + offline static validation fallback
set -euo pipefail

docker_daemon_ready() {
  command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1
}

docker_static_verify() {
  local root="$1"
  local compose_file="${2:-$root/infra/docker/docker-compose.yml}"
  local log="${3:-/dev/stdout}"

  {
    echo "▶ docker compose config (static)"
    docker compose -f "$compose_file" config --quiet
    echo "  ✅ compose config valid"

    echo "▶ Dockerfile presence"
    local dockerfiles=(
      "$root/services/onboarding-api/Dockerfile"
      "$root/clients/node-cli/Dockerfile"
      "$root/engines/rust-analyzer/Dockerfile"
    )
    for df in "${dockerfiles[@]}"; do
      if [[ ! -f "$df" ]]; then
        echo "  ❌ missing: $df"
        return 1
      fi
      echo "  ✅ $(basename "$(dirname "$df")")/Dockerfile"
    done

    echo "▶ compose service definitions"
    for svc in onboarding-api postgres prometheus grafana; do
      if ! grep -q "^  ${svc}:" "$compose_file"; then
        echo "  ❌ missing service: $svc"
        return 1
      fi
      echo "  ✅ service: $svc"
    done
  } >>"$log" 2>&1
}
