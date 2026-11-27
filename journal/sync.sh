#!/usr/bin/env bash
# Keep the trade journal on its own data branch so trading runs never push to main.
#   journal/sync.sh pull          -> checks out the latest journal into /tmp/trade-journal, prints the CSV path
#   journal/sync.sh push "msg"    -> commits and pushes /tmp/trade-journal to origin claude/trade-journal
set -euo pipefail
BR=claude/trade-journal; WT=/tmp/trade-journal
cd "$(git rev-parse --show-toplevel)"
case "${1:-}" in
  pull)
    git worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
    if git fetch -q origin "$BR" 2>/dev/null; then git worktree add -q --detach "$WT" FETCH_HEAD
    else git worktree add -q --detach "$WT" HEAD; fi
    echo "$WT/journal/trades.csv" ;;
  push)
    cd "$WT"; git add journal/trades.csv
    git diff --cached --quiet && { echo "journal unchanged"; exit 0; }
    git commit -q -m "${2:-Update trade journal}"
    for i in 1 2 3 4; do git push -q origin "HEAD:refs/heads/$BR" && { echo "pushed to $BR"; exit 0; }; sleep $((2**i)); done
    echo "push failed" >&2; exit 1 ;;
  *) echo "usage: $0 pull|push [msg]" >&2; exit 2 ;;
esac
