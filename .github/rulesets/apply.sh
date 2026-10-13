#!/usr/bin/env sh
# Create or update this repository's branch protection rulesets.
#
# Run by a human, deliberately. Nothing in CI calls this.
#
# B through F ship at "enforcement": "evaluate" -- they log what they would
# have blocked and block nothing. A is "active" and running this makes it so:
# a pull request, a signature and seven checks become mandatory on the default
# branch, for every contributor and every session already in flight. Read
# README.md's ordering traps first.
set -eu

REPO="${REPO:-quaternionmedia/qm}"
DIR="$(dirname "$0")"

command -v gh >/dev/null || { echo "gh CLI not found"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated"; exit 1; }

existing="$(gh api "repos/$REPO/rulesets" --jq '.[] | "\(.id)\t\(.name)"' 2>/dev/null || true)"

# [A-Z], not a hand-maintained range: F-tags.json was added while this glob
# still read [A-E], so the version-tags ruleset was never created and nothing
# said so. A ruleset that is never applied is indistinguishable from one that
# is applied and permits everything.
for f in "$DIR"/[A-Z]-*.json; do
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
echo "Read the [enforcement] column above: active enforces, evaluate only logs."
echo "Check what they would have blocked:"
echo "  gh api \"repos/$REPO/rulesets/rule-suites\""
