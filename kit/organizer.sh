#!/usr/bin/env bash
# organizer.sh — sort files from inbox/ into the workspace (rules: docs/PROTOCOL.md).
# Preview by default. Never deletes. Never overwrites. Never reads file contents.
# Usage: bash tools/organizer.sh            preview
#        bash tools/organizer.sh --apply    move + write undo script + log
set -u

APPLY=0
case "${1:-}" in
  "") ;;
  --apply) APPLY=1 ;;
  *) echo "Usage: organizer.sh [--apply]"; exit 2 ;;
esac

ROOT="${WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
INBOX="$ROOT/inbox"
[ -d "$INBOX" ] || { echo "ERROR: $INBOX not found. Run bootstrap.sh first."; exit 1; }

TS=$(date +%Y%m%d-%H%M%S)
UNDO="$ROOT/recovery/undo-$TS.sh"
MOVED=0
SKIPPED=0

lower() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]'; }

is_secret() {
  case "$1" in
    .env*|*.pem|*.key|*.p12|*.pfx|*.kdbx|id_rsa*|id_ed25519*|*credential*|*secret*|*token*) return 0 ;;
  esac
  return 1
}

dest_for_ext() {
  case "$1" in
    md|txt|rst)                                   echo "docs/notes" ;;
    pdf|doc|docx|pptx|epub)                       echo "docs/research" ;;
    png|jpg|jpeg|gif|svg|webp)                    echo "docs/assets" ;;
    py|js|ts|sh|go|rs|java|c|cpp|rb|php|html|css) echo "sandbox/code" ;;
    csv|tsv|xlsx|json|yaml|yml|xml|sql)           echo "sandbox/data" ;;
    zip|tar|gz|tgz|7z)                            echo "sandbox/archives" ;;
    log)                                          echo "sandbox/logs" ;;
    *)                                            echo "" ;;
  esac
}

skip() { echo "SKIP  $1  ($2)"; SKIPPED=$((SKIPPED + 1)); }

while IFS= read -r -d '' f; do
  base=$(basename "$f")
  low=$(lower "$base")

  case "$base" in .gitkeep|README*|_unsorted) continue ;; esac
  if [ -L "$f" ]; then skip "$base" "symlink"; continue; fi
  if is_secret "$low"; then skip "$base" "SECRET-LIKE, left in place"; continue; fi
  if [ -d "$f" ]; then skip "$base" "directory, ask KAGEROU"; continue; fi
  case "$base" in .*) skip "$base" "hidden file"; continue ;; esac

  name="$base"
  dest=""

  # project routing: <project>__name.ext
  case "$base" in
    *__*)
      proj="${base%%__*}"
      rest="${base#*__}"
      if [ -n "$proj" ] && [ -n "$rest" ] && [ -d "$ROOT/projects/$proj" ]; then
        dest="projects/$proj"
        name="$rest"
      fi
      ;;
  esac

  if [ -z "$dest" ]; then
    case "$low" in *.*) ext="${low##*.}" ;; *) ext="" ;; esac
    dest=$(dest_for_ext "$ext")
    if [ -z "$dest" ]; then skip "$base" "unknown type"; continue; fi
  fi

  target="$ROOT/$dest/$name"
  if [ -e "$target" ]; then
    case "$name" in
      *.*) target="$ROOT/$dest/${name%.*}-$TS.${name##*.}" ;;
      *)   target="$ROOT/$dest/$name-$TS" ;;
    esac
  fi

  echo "MOVE  $base  ->  ${target#"$ROOT"/}"

  if [ "$APPLY" = 1 ]; then
    mkdir -p "$ROOT/$dest" "$ROOT/recovery"
    if mv -n "$f" "$target" && [ -e "$target" ] && [ ! -e "$f" ]; then
      [ -f "$UNDO" ] || printf '#!/usr/bin/env bash\n# undo for organizer run %s\n' "$TS" > "$UNDO"
      printf 'mv -n %q %q\n' "$target" "$f" >> "$UNDO"
      MOVED=$((MOVED + 1))
    else
      echo "FAIL  $base  (move not confirmed)"
      SKIPPED=$((SKIPPED + 1))
    fi
  else
    MOVED=$((MOVED + 1))
  fi
done < <(find "$INBOX" -maxdepth 1 -mindepth 1 -print0 | sort -z)

if [ "$APPLY" = 1 ]; then
  if [ "$MOVED" -gt 0 ]; then
    chmod +x "$UNDO" 2>/dev/null
    mkdir -p "$ROOT/docs"
    echo "- $TS moved $MOVED, skipped $SKIPPED (undo: recovery/undo-$TS.sh)" >> "$ROOT/docs/organizer-log.md"
    echo "UNDO: bash recovery/undo-$TS.sh"
  fi
  echo "MODE: APPLIED | MOVED: $MOVED | SKIPPED: $SKIPPED"
else
  echo "MODE: DRY-RUN | WOULD MOVE: $MOVED | SKIPPED: $SKIPPED"
  echo "Preview only. Run with --apply to move."
fi
exit 0
