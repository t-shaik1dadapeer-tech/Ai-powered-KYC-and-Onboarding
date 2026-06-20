# GitHub Push Setup (one time)

GitHub asks for credentials repeatedly when no credential helper is configured.  
Follow these steps **once** — after that `make push` works without re-entering your token.

## Step 1 — Create a Personal Access Token

1. Open https://github.com/settings/tokens  
2. **Generate new token (classic)**  
3. Enable scope: **`repo`**  
4. Copy the token (starts with `ghp_`)

## Step 2 — Save credentials locally (not in the repo)

```bash
cp .github-credentials.env.example ~/.github-credentials.env
```

Edit `~/.github-credentials.env`:

```
GITHUB_USER=t-shaik1dadapeer-tech
GITHUB_TOKEN=ghp_your_token_here
```

This file lives in your **home directory** — it is never committed.

## Step 3 — Run one-time setup

```bash
cd "/Users/shaikdadapeer/agent development"
make setup-github
```

Expected output: `SUCCESS — GitHub auth is configured`

This stores your token in **macOS Keychain** via `git credential osxkeychain`.

## Step 4 — Push

```bash
# First push (if GitHub only has README):
make push-first

# Every later push:
git add ...
git commit -m "your message"
make push
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Asked for password every push | Re-run `make setup-github` |
| `Authentication failed` | Regenerate PAT with `repo` scope |
| `remote origin already exists` | Normal — run `make setup-github` anyway |
| SSH timeout on port 22 | Use HTTPS setup above (recommended) |
| `Permission denied` | Ensure token owner has write access to the repo |

## What gets configured

| Setting | Value |
|---------|-------|
| `credential.helper` | `osxkeychain` (global) |
| `credential.useHttpPath` | `true` |
| `origin` | `https://github.com/t-shaik1dadapeer-tech/Ai-powered-KYC-and-Onboarding.git` |
