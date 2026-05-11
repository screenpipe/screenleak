#!/usr/bin/env bash
# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
#
# pre_oss_check.sh — final sanity sweep before flipping the repo public.
#
# Two-zone model:
#   - SOURCE/DOC zone: code + docs. Real-looking secrets/emails/SSNs here = error.
#   - BENCH-DATA zone: text/data/, image/corpus/, image/templates/, trace/data/,
#     */results/ — these are FULL of synthetic-realistic strings on purpose.
#     Bench data is allowed real-looking strings IFF every match contains a
#     synthetic marker (FAKE/example/test/invalid).
#
# We always exclude .git/, .venv/, node_modules/, __pycache__/.

set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

errors=0
warns=0

err()  { echo "  ❌ $*" >&2; errors=$((errors + 1)); }
warn() { echo "  ⚠️  $*" >&2; warns=$((warns + 1)); }
ok()   { echo "  ✅ $*"; }

# Common grep excludes — applied to every scan.
GREP_EXCLUDES=(
  --exclude-dir=.git
  --exclude-dir=.venv
  --exclude-dir=venv
  --exclude-dir=node_modules
  --exclude-dir=__pycache__
  --exclude-dir=.ruff_cache
  --exclude-dir=.pytest_cache
)

# Bench-data zone — code/doc checks skip these, but they get their own
# stricter "every match must contain a synthetic marker" pass.
BENCH_DATA_EXCLUDES=(
  --exclude-dir=data           # text/data, trace/data
  --exclude-dir=corpus         # image/corpus
  --exclude-dir=templates      # image/templates
  --exclude-dir=results        # */results
)

# Markers that prove a string is intentionally synthetic.
SYNTH_MARKERS='FAKE|fake|example\.|\.example|\.test\b|\.invalid\b|EXAMPLE|@example\.|@beispiel\.|@exemple\.|tessera|helios-ai|gracenote|photon-labs|wavelet-vision|123-45-6789|555-01[0-9][0-9]'

# Load the synthetic-data allowlist. Files listed here are exempt from the
# secret/PII checks because they're deliberately full of synthetic-realistic
# strings used as bench fixtures. Add new entries with care.
ALLOWLIST=()
if [[ -f .synth-allowlist ]]; then
  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    ALLOWLIST+=("$line")
  done < .synth-allowlist
fi
is_allowlisted() {
  local f="${1#./}"
  for a in "${ALLOWLIST[@]}"; do
    [[ "$f" == "$a" ]] && return 0
  done
  return 1
}


echo "[pre-oss] required files"
for f in README.md LICENSE LICENSE-DATA CITATION.bib METHODOLOGY.md THREAT_MODEL.md CATEGORIES.md LIMITATIONS.md SOURCES.md CONTRIBUTING.md SECURITY.md; do
  if [[ -f "$f" ]]; then ok "$f"; else err "missing: $f"; fi
done

echo
echo "[pre-oss] hardcoded local paths in source / docs (bench-data zone exempt)"
hits=$(grep -rEln --no-messages \
  "${GREP_EXCLUDES[@]}" "${BENCH_DATA_EXCLUDES[@]}" \
  --exclude='PROVENANCE.md' --exclude='SOURCES.md' \
  --exclude='Makefile' --exclude='ROADMAP.md' --exclude='*.lock' \
  '/Users/[a-zA-Z0-9._-]+' . 2>/dev/null || true)
if [[ -z "$hits" ]]; then
  ok "no hardcoded /Users/ paths in source/docs"
else
  warn "hardcoded paths in:"
  echo "$hits" | sed 's/^/      /' >&2
fi

echo
echo "[pre-oss] real-looking secrets in source / docs"
patterns='sk-[a-zA-Z0-9]{20,}|sk-ant-[a-zA-Z0-9-]{20,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+'
hits=$(grep -rEln --no-messages \
  "${GREP_EXCLUDES[@]}" "${BENCH_DATA_EXCLUDES[@]}" \
  "$patterns" . 2>/dev/null || true)
if [[ -z "$hits" ]]; then
  ok "no real-looking secrets in source/docs"
else
  bad=""
  for f in $hits; do
    if is_allowlisted "$f"; then continue; fi
    nb=$(grep -E "$patterns" "$f" | grep -Ev "$SYNTH_MARKERS" || true)
    if [[ -n "$nb" ]]; then bad+="$f"$'\n'; fi
  done
  if [[ -z "$bad" ]]; then
    ok "secret-shaped strings in source/docs are synthetic or allowlisted"
  else
    err "non-synthetic secrets in:"
    echo "$bad" | sed 's/^/      /' >&2
  fi
fi

echo
echo "[pre-oss] real-looking secrets in bench data (must all be synthetic-marked)"
hits=$(grep -rEln --no-messages \
  "${GREP_EXCLUDES[@]}" \
  "$patterns" \
  text/data image/corpus image/templates trace/data 2>/dev/null || true)
if [[ -z "$hits" ]]; then
  ok "no secret-shaped strings in bench data"
else
  bad=""
  for f in $hits; do
    if is_allowlisted "$f"; then continue; fi
    nb=$(grep -E "$patterns" "$f" | grep -Ev "$SYNTH_MARKERS" || true)
    if [[ -n "$nb" ]]; then bad+="$f"$'\n'; fi
  done
  if [[ -z "$bad" ]]; then
    ok "secret-shaped strings in bench data are synthetic-marked or allowlisted"
  else
    err "non-synthetic secret-shapes in bench data:"
    echo "$bad" | sed 's/^/      /' >&2
  fi
fi

echo
echo "[pre-oss] real-looking PII (emails on public TLDs, non-fake SSNs) in source/docs"
email_re='[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|org|io|net|co|me|dev|app|ai)\b'
hits=$(grep -rEln --no-messages \
  "${GREP_EXCLUDES[@]}" "${BENCH_DATA_EXCLUDES[@]}" \
  "$email_re" . 2>/dev/null || true)
bad=""
for f in $hits; do
  [[ -z "$f" ]] && continue
  if is_allowlisted "$f"; then continue; fi
  # Lines with the canonical contact email or any synthetic marker pass.
  nb=$(grep -E "$email_re" "$f" \
        | grep -v "louis@screenpi.pe" \
        | grep -v "noreply@" \
        | grep -Ev "$SYNTH_MARKERS" || true)
  if [[ -n "$nb" ]]; then bad+="$f"$'\n'; fi
done
if [[ -z "$bad" ]]; then
  ok "no non-synthetic public-TLD emails in source/docs"
else
  warn "public-TLD emails in:"
  echo "$bad" | sed 's/^/      /' >&2
fi

ssn_hits=$(grep -rEln --no-messages \
  "${GREP_EXCLUDES[@]}" "${BENCH_DATA_EXCLUDES[@]}" \
  '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b' . 2>/dev/null || true)
if [[ -z "$ssn_hits" ]]; then
  ok "no SSN-shaped strings in source/docs"
else
  bad=""
  for f in $ssn_hits; do
    nb=$(grep -E '[0-9]{3}-[0-9]{2}-[0-9]{4}' "$f" | grep -v '123-45-6789' || true)
    if [[ -n "$nb" ]]; then bad+="$f"$'\n'; fi
  done
  if [[ -z "$bad" ]]; then
    ok "only synthetic SSN (123-45-6789) in source/docs"
  else
    err "non-canonical SSN-shapes in source/docs:"
    echo "$bad" | sed 's/^/      /' >&2
  fi
fi

echo
echo "[pre-oss] repo size"
size_kb=$(du -sk --exclude='.venv' --exclude='.git' --exclude='node_modules' . 2>/dev/null | awk '{print $1}' || du -sk . | awk '{print $1}')
size_mb=$((size_kb / 1024))
if (( size_mb > 200 )); then
  warn "repo is ${size_mb}MB (excluding .venv/.git) — consider IMAGES=skip or LFS"
elif (( size_mb > 50 )); then
  ok "repo is ${size_mb}MB excluding .venv/.git (acceptable for OSS)"
else
  ok "repo is ${size_mb}MB excluding .venv/.git (light)"
fi

echo
echo "[pre-oss] .venv / .git / node_modules excluded from git"
gi_ok=true
for pat in ".venv" "node_modules" "__pycache__" ".env" ".env.local"; do
  if ! grep -q "^${pat}/" .gitignore 2>/dev/null && ! grep -q "^${pat}\$" .gitignore 2>/dev/null; then
    warn "$pat not in .gitignore"
    gi_ok=false
  fi
done
$gi_ok && ok ".gitignore covers .venv / node_modules / __pycache__ / .env"

echo
echo "[pre-oss] gold integrity (trace bench)"
if [[ -f trace/data/injected_val.jsonl ]]; then
  python3 -c "
import json, sys
fails = 0; total = 0
for path in ('trace/data/injected_train.jsonl', 'trace/data/injected_val.jsonl'):
    try:
        for line in open(path):
            if not line.strip(): continue
            row = json.loads(line)
            tool_content = row['messages'][row['injected_tool_idx']]['content']
            for item in row['injected_pii']:
                total += 1
                if item['text'] not in tool_content:
                    fails += 1
    except FileNotFoundError:
        pass
print(f'  gold items: {total}, mismatches: {fails}')
sys.exit(1 if fails > 0 else 0)
" && ok "gold integrity verified" || err "gold integrity broken"
else
  warn "no trace data yet — run 'make trace-data'"
fi

echo
echo "[pre-oss] summary: ${errors} errors, ${warns} warnings"
if (( errors > 0 )); then
  echo "FAIL — fix errors before going public" >&2
  exit 1
fi
echo "OK"
