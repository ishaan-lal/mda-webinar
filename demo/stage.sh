#!/usr/bin/env bash
# Build Patch in front of an audience, one stage at a time.
#
#   ./stage.sh reset   start over: patch/ holds only the bare agent (stage 1)
#   ./stage.sh next    apply the next stage, printing what it changes
#   ./stage.sh 5       apply stage 5 (must be the next one)
#   ./stage.sh all     reset, then apply every stage (the finished agent)
#   ./stage.sh status  show which stage patch/ is at
#
# A stage is a folder under stages/. Its files are copied into patch/, except
# `*.append` files, which are appended to the file of the same name.
# reset keeps patch/.env and patch/.venv, and wipes patch/.mda (local memory,
# threads, and build output), so every run starts from a clean agent.
set -euo pipefail
cd "$(dirname "$0")"

STAGES=stages
WORK=patch
MARKER="$WORK/.stage"

stage_dir() {
  local dir
  dir=$(ls -d "$STAGES/$(printf '%02d' "$1")"-* 2>/dev/null | head -n1)
  [ -n "$dir" ] || { echo "No stage $1 in $STAGES/." >&2; exit 1; }
  echo "$dir"
}

current() { cat "$MARKER" 2>/dev/null || echo 0; }
last() { ls -d "$STAGES"/[0-9][0-9]-* | wc -l | tr -d ' '; }

show_diff() {
  # git diff --no-index exits 1 when the files differ.
  git --no-pager diff --no-index --color=always "$1" "$2" | tail -n +5 || true
}

apply() {
  local n=$1 dir rel target
  local expected=$(( $(current) + 1 ))
  if [ "$n" -ne "$expected" ]; then
    echo "patch/ is at stage $(current), so the next stage is $expected (not $n)." >&2
    echo "Run ./stage.sh reset to start over." >&2
    exit 1
  fi
  dir=$(stage_dir "$n")
  printf '\n\033[1m== Stage %s: %s ==\033[0m\n' "$n" "${dir#"$STAGES"/??-}"
  while IFS= read -r rel; do
    if [[ "$rel" == *.append ]]; then
      target="$WORK/${rel%.append}"
      printf '\n\033[33m~ %s\033[0m (appended)\n' "${rel%.append}"
      cat "$dir/$rel" >> "$target"
      sed 's/^/  + /' "$dir/$rel"
    elif [ -e "$WORK/$rel" ]; then
      printf '\n\033[33m~ %s\033[0m\n' "$rel"
      show_diff "$WORK/$rel" "$dir/$rel"
      cp "$dir/$rel" "$WORK/$rel"
    else
      printf '\033[32m+ %s\033[0m\n' "$rel"
      mkdir -p "$(dirname "$WORK/$rel")"
      cp -p "$dir/$rel" "$WORK/$rel"
    fi
  done < <(cd "$dir" && find . -type f ! -name .DS_Store | sed 's|^\./||' | sort)
  echo "$n" > "$MARKER"
  printf '\nNow at stage %s of %s. Restart `uv run mda dev` to pick it up.\n' "$n" "$(last)"
}

reset() {
  mkdir -p "$WORK"
  # Remove everything except secrets and the virtualenv.
  find "$WORK" -mindepth 1 -maxdepth 1 ! -name .env ! -name .venv -exec rm -rf {} +
  echo 0 > "$MARKER"
  apply 1 > /dev/null
  echo "patch/ reset to stage 1 (the bare agent)."
}

case "${1:-}" in
  reset) reset ;;
  next) apply $(( $(current) + 1 )) ;;
  all)
    reset
    for n in $(seq 2 "$(last)"); do apply "$n" > /dev/null; done
    echo "patch/ now holds the finished agent (stage $(last))."
    ;;
  status) echo "patch/ is at stage $(current) of $(last)." ;;
  ''|-h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//' ;;
  *[!0-9]*) echo "Unknown command: $1" >&2; exit 1 ;;
  *) apply "$1" ;;
esac
