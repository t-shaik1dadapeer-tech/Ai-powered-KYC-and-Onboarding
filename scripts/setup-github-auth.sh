#!/usr/bin/env bash
# One-time GitHub auth setup — after this, git push should not ask repeatedly.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CREDS_FILE="${GITHUB_CREDENTIALS_FILE:-$HOME/.github-credentials.env}"
REMOTE="${GITHUB_REMOTE:-https://github.com/t-shaik1dadapeer-tech/Ai-powered-KYC-and-Onboarding.git}"

log() { echo "[setup-github] $*"; }
die() { echo "[setup-github] ERROR: $*" >&2; exit 1; }

log "Configuring Git credential storage (macOS Keychain)..."
git config --global credential.helper osxkeychain
git config --global credential.useHttpPath true

log "Ensuring origin remote is set..."
cd "$ROOT"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE"
else
  git remote add origin "$REMOTE"
fi
log "  origin → $(git remote get-url origin)"

if [[ -f "$CREDS_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CREDS_FILE"
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    GITHUB_USER="${GITHUB_USER:-t-shaik1dadapeer-tech}"
    log "Seeding Keychain from $CREDS_FILE (token found)..."
    printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n' \
      "$GITHUB_USER" "$GITHUB_TOKEN" | git credential approve
    log "  Keychain updated for github.com"
  else
    die "GITHUB_TOKEN missing in $CREDS_FILE"
  fi
else
  log ""
  log "No credentials file yet: $CREDS_FILE"
  log "Create it once (see .github-credentials.env.example), then re-run:"
  log "  make setup-github"
  log ""
  log "Or authenticate interactively (one time only):"
  log "  git ls-remote origin"
  log "  Username → your GitHub username"
  log "  Password → Personal Access Token (NOT your GitHub password)"
  log "  Create token: https://github.com/settings/tokens (classic, repo scope)"
  exit 0
fi

log "Testing connection to GitHub..."
if git ls-remote origin HEAD >/dev/null 2>&1; then
  log "SUCCESS — GitHub auth is configured. Use: make push"
else
  die "git ls-remote failed — check GITHUB_TOKEN and repo access"
fi
