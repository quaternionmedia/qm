#!/usr/bin/env sh
# Create or update this repository's branch protection rulesets.
#
# Run by a human, deliberately. Nothing in CI calls this.
#
# All five configs ship at "enforcement": "evaluate" -- they log what they
# would have blocked and block nothing. Read README.md's ordering traps before
# promoting any of them to "active".
set -eu

REPO="${REPO:-quaternionmedia/qm}"
DIR="$(dirname "$0")"

command -v gh >/dev/null || { echo "gh CLI not found"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated"; exit 1; }

existing="$(gh api "repos/$REPO/rulesets" --jq '.[] | "\(.id)\t\(.name)"' 2>/dev/null || true)"

for f in "$DIR"/[A-E]-*.json; do
  name="$(python -c "import json,sys;print(json.load(open(sys.argv[1]))['name'])" "$f")"
  id="$(printf '%s\n' "$existing" | awk -F'\t' -v n="$name" '$2==n {print $1}')"

  if [ -n "$id" ]; then
    echo "updating  $name  (id $id)"
    gh api --silent -X PUT "repos/$REPO/rulesets/$id" --input "$f"
  else
    echo "creating  $name"
    gh api --silent -X POST "repos/$REPO/rulesets" --input "$f"
  fi
done

echo
echo "Current rulesets:"
gh api "repos/$REPO/rulesets" --jq '.[] | "  \(.name)  [\(.enforcement)]"'
echo
echo "These are evaluating, not enforcing, unless a config says otherwise."
echo "Check what they would have blocked:"
echo "  gh api \"repos/$REPO/rulesets/rule-suites\""
