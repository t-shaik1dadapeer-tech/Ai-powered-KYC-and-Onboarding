#!/usr/bin/env bash
# Reproducible git worktree demo — analysis + observability parallel streams
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/worktrees"
LOG="$EVIDENCE/phase-11-worktree-demo.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ANALYSIS_WT="$ROOT/.worktrees/analysis"
OBS_WT="$ROOT/.worktrees/observability"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Worktree Demo — $TIMESTAMP"
log "=========================="
log ""

cd "$ROOT"

if [[ ! -d .git ]]; then
  log "▶ git init"
  git init -b main >> "$LOG" 2>&1
  git add -A
  git commit -m "chore: initial platform snapshot (phases 0-10)" >> "$LOG" 2>&1
  log "  ✅ Initial commit on main"
else
  log "▶ git repo exists"
  if ! git rev-parse HEAD >/dev/null 2>&1; then
    git add -A
    git commit -m "chore: initial platform snapshot (phases 0-10)" >> "$LOG" 2>&1
    log "  ✅ Initial commit on main"
  else
    log "  ✅ HEAD exists: $(git rev-parse --short HEAD)"
  fi
fi

log ""
log "▶ Create branches (if missing)"
git show-ref --verify --quiet refs/heads/analysis-worktree || git branch analysis-worktree
git show-ref --verify --quiet refs/heads/observability-worktree || git branch observability-worktree
log "  ✅ Branches: analysis-worktree, observability-worktree"

log ""
log "▶ Add worktrees"
if [[ ! -d "$ANALYSIS_WT" ]]; then
  git worktree add "$ANALYSIS_WT" analysis-worktree >> "$LOG" 2>&1
  log "  ✅ Created $ANALYSIS_WT"
else
  log "  ⏭ analysis worktree exists"
fi

if [[ ! -d "$OBS_WT" ]]; then
  git worktree add "$OBS_WT" observability-worktree >> "$LOG" 2>&1
  log "  ✅ Created $OBS_WT"
else
  log "  ⏭ observability worktree exists"
fi

log ""
log "▶ Commit demo change in analysis worktree"
ANALYSIS_MARKER="$ANALYSIS_WT/engines/intelligence/WORKTREE_MARKER.md"
if [[ ! -f "$ANALYSIS_MARKER" ]]; then
  cat > "$ANALYSIS_MARKER" <<MARKER
# Analysis Worktree Marker

- **Branch:** analysis-worktree
- **Purpose:** Parallel intelligence / flow-tracing development
- **Demo run:** $TIMESTAMP
- **Isolation:** No edits to infra/grafana or app/core/metrics.py from this stream
MARKER
  git -C "$ANALYSIS_WT" add engines/intelligence/WORKTREE_MARKER.md
  git -C "$ANALYSIS_WT" commit -m "docs(intelligence): analysis worktree demo marker" >> "$LOG" 2>&1
  log "  ✅ Analysis worktree commit"
else
  log "  ⏭ Analysis marker already present"
fi

log ""
log "▶ Commit demo change in observability worktree"
OBS_MARKER="$OBS_WT/docs/observability/WORKTREE_MARKER.md"
if [[ ! -f "$OBS_MARKER" ]]; then
  cat > "$OBS_MARKER" <<MARKER
# Observability Worktree Marker

- **Branch:** observability-worktree
- **Purpose:** Parallel metrics / Grafana / Prometheus development
- **Demo run:** $TIMESTAMP
- **Isolation:** No edits to engines/intelligence/src from this stream
MARKER
  git -C "$OBS_WT" add docs/observability/WORKTREE_MARKER.md
  git -C "$OBS_WT" commit -m "docs(observability): observability worktree demo marker" >> "$LOG" 2>&1
  log "  ✅ Observability worktree commit"
else
  log "  ⏭ Observability marker already present"
fi

log ""
log "▶ Merge analysis-worktree → main"
git checkout main >> "$LOG" 2>&1
if git merge-base --is-ancestor analysis-worktree main 2>/dev/null; then
  log "  ⏭ analysis-worktree already merged"
else
  git merge --no-ff analysis-worktree -m "merge: analysis-worktree into main" >> "$LOG" 2>&1
  log "  ✅ Merged analysis-worktree"
fi

log ""
log "▶ Merge observability-worktree → main"
if git merge-base --is-ancestor observability-worktree main 2>/dev/null; then
  log "  ⏭ observability-worktree already merged"
else
  git merge --no-ff observability-worktree -m "merge: observability-worktree into main" >> "$LOG" 2>&1
  log "  ✅ Merged observability-worktree"
fi

log ""
log "▶ Worktree list"
git worktree list | tee -a "$LOG"

log ""
log "▶ Recent merge history"
git log --oneline --graph -8 | tee -a "$LOG"

log ""
log "=========================="
log "✅ Worktree demo complete"
log "Docs: docs/worktrees/"
log "Evidence: $LOG"
