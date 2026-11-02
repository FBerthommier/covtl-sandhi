#!/usr/bin/env sh
# covtl-sandhi v0.1.0 — official installation procedure (Branch A + Branch B)
#
# Chains: clone covtl-pipeline -> apply the hook patch (Branch A) ->
#         pip install -e . (pipeline) -> activate Branch B (copy or pip) ->
#         run the standalone test suite (38 tests expected).
#
# Usage:
#   ./install.sh [pipeline_dir] [copy|pip] [pipeline_ref]
#
#   pipeline_dir   where to clone the pipeline (default: ./covtl-pipeline
#                  next to this script)
#   copy|pip       Branch B activation mode (default: copy — recommended)
#   pipeline_ref   optional commit to pin, e.g. f60c73e (hook merged in
#                  main) or 181c272 (last pre-hook main). Empty = track
#                  the remote default branch.
#
# NOTE: never run `cp -r sandhi/ dst/` — the trailing `/.` in the copy below
# is what copies the CONTENT of sandhi/ into the stub folder instead of
# nesting the folder one level too deep.

set -e

SANDHI_DIR="$(cd "$(dirname "$0")" && pwd)"
PIPELINE_URL="${PIPELINE_URL:-https://github.com/FBerthommier/covtl-pipeline.git}"
PIPELINE_DIR="${1:-$SANDHI_DIR/covtl-pipeline}"
BRANCH_B="${2:-copy}"
PIPELINE_REF="${3:-}"

echo "== covtl-sandhi v0.1.0 installer =="
echo "   package : $SANDHI_DIR"
echo "   pipeline: $PIPELINE_DIR  ($BRANCH_B activation)"

# --- 0) prerequisites -------------------------------------------------------
command -v git  >/dev/null 2>&1 || { echo "ERROR: git not found";  exit 1; }
command -v python >/dev/null 2>&1 || { echo "ERROR: python not found"; exit 1; }

# --- 1) clone the pipeline (Branch A target) --------------------------------
if [ ! -d "$PIPELINE_DIR/.git" ]; then
    git clone "$PIPELINE_URL" "$PIPELINE_DIR"
else
    echo "-- pipeline already cloned at $PIPELINE_DIR (skipping clone)"
fi

if [ -n "$PIPELINE_REF" ]; then
    git -C "$PIPELINE_DIR" checkout "$PIPELINE_REF"
fi

# --- 2) apply the hook patch (Branch A) --------------------------------------
# Idempotent: skip with a notice if the patch is already applied.
PATCH="$SANDHI_DIR/patch/covtl-pipeline-sandhi-hook.patch"
if git -C "$PIPELINE_DIR" apply --check "$PATCH" 2>/dev/null; then
    git -C "$PIPELINE_DIR" apply "$PATCH"
    echo "-- hook patch applied (Branch A: stub + --sandhi/--sandhi-mode options)"
elif git -C "$PIPELINE_DIR" apply --reverse --check "$PATCH" 2>/dev/null; then
    echo "-- hook patch already applied (skipping)"
else
    echo "ERROR: patch does not apply cleanly — pipeline tree has drifted."
    echo "       Try pinning a known baseline: ./install.sh '' copy f60c73e"
    exit 1
fi

# --- 3) install the pipeline itself (editable, as for the bare repo) --------
python -m pip install -e "$PIPELINE_DIR"

# --- 4) activate Branch B (the rules) — copy (recommended) or pip -----------
STUB_DIR="$PIPELINE_DIR/vtl_synth/utils/sandhi"
if [ "$BRANCH_B" = "copy" ]; then
    # The stub folder already exists: copy the CONTENT of sandhi/ (note the '/.').
    mkdir -p "$STUB_DIR"
    cp -r "$SANDHI_DIR/sandhi/." "$STUB_DIR/"
    echo "-- Branch B activated by copy: stub overwritten, SANDHI_FULL = True"
else
    python -m pip install "$SANDHI_DIR"
    echo "-- Branch B activated by pip install (hook resolves via site-packages)"
fi

# --- 5) verify ---------------------------------------------------------------
echo "-- running the standalone package test suite (expect: 38 passed)"
cd "$SANDHI_DIR"
python -m pytest tests/ -q

cat <<'EOF'

== smoke tests (require the pipeline installed above) ==
  vtl-synth run "faut il"    -l fr --sandhi standard --no-video -o out   # fo.til
  vtl-synth run "far away"   -l en --sandhi standard --no-video -o out   # fa.R@.we
  vtl-synth run "los amigos" -l es --sandhi standard --no-video -o out   # lo.sa.mi.gos
  vtl-synth run "os amigos"  -l pt --sandhi standard --no-video -o out   # o.Z@.mi.guS
  vtl-synth run "a casa"     -l it --sandhi standard --no-video -o out   # a.kka.sa
  vtl-synth run "ein Apfel"  -l de --sandhi standard --no-video -o out   # ajn a.pf@l
== done ==
EOF
