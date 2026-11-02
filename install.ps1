# covtl-sandhi v0.1.0 - official installation procedure (Branch A + Branch B)
#
# Chains: clone covtl-pipeline -> apply the hook patch (Branch A) ->
#         pip install -e . (pipeline) -> activate Branch B (copy or pip) ->
#         run the standalone test suite (38 tests expected).
#
# Usage:
#   .\install.ps1 [[-PipelineDir] <path>] [[-BranchB] copy|pip] [[-PipelineRef] <commit>]
#
#   -PipelineDir   where to clone the pipeline (default: .\covtl-pipeline
#                  next to this script)
#   -BranchB       activation mode (default: copy - recommended)
#   -PipelineRef   optional commit to pin, e.g. f60c73e (hook merged in
#                  main) or 181c272 (last pre-hook main). Empty = track
#                  the remote default branch.
#
# NOTE: the copy below uses sandhi\* (NOT sandhi) so that the CONTENT of
# sandhi\ lands in the stub folder instead of nesting the folder one level
# too deep (the PowerShell equivalent of `cp -r sandhi/. dst/`).

[CmdletBinding()]
param(
    [string]$PipelineDir = "",
    [ValidateSet('copy', 'pip')]
    [string]$BranchB = 'copy',
    [string]$PipelineRef = "",
    [string]$PipelineUrl = "https://github.com/FBerthommier/covtl-pipeline.git"
)

$ErrorActionPreference = 'Stop'
$Sandbox = $PSScriptRoot
if (-not $PipelineDir) { $PipelineDir = Join-Path $Sandbox 'covtl-pipeline' }

Write-Host "== covtl-sandhi v0.1.0 installer =="
Write-Host "   package : $Sandbox"
Write-Host "   pipeline: $PipelineDir  ($BranchB activation)"

# --- 0) prerequisites ---------------------------------------------------------
foreach ($tool in 'git', 'python') {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "ERROR: $tool not found"
    }
}

# --- 1) clone the pipeline (Branch A target) -----------------------------------
if (-not (Test-Path (Join-Path $PipelineDir '.git'))) {
    git clone $PipelineUrl $PipelineDir
} else {
    Write-Host "-- pipeline already cloned at $PipelineDir (skipping clone)"
}

if ($PipelineRef) {
    git -C $PipelineDir checkout $PipelineRef
}

# --- 2) apply the hook patch (Branch A) ------------------------------------------
# Idempotent: skip with a notice if the patch is already applied.
$patch = Join-Path $Sandbox 'patch\covtl-pipeline-sandhi-hook.patch'
git -C $PipelineDir apply --check $patch 2>$null
$appliesClean = ($LASTEXITCODE -eq 0)
git -C $PipelineDir apply --reverse --check $patch 2>$null
$alreadyApplied = ($LASTEXITCODE -eq 0)

if ($appliesClean) {
    git -C $PipelineDir apply $patch
    Write-Host "-- hook patch applied (Branch A: stub + --sandhi/--sandhi-mode options)"
} elseif ($alreadyApplied) {
    Write-Host "-- hook patch already applied (skipping)"
} else {
    throw @"
ERROR: patch does not apply cleanly - pipeline tree has drifted.
       Try pinning a known baseline: .\install.ps1 -PipelineRef f60c73e
"@
}

# --- 3) install the pipeline itself (editable, as for the bare repo) ------------
python -m pip install -e $PipelineDir

# --- 4) activate Branch B (the rules) - copy (recommended) or pip ----------------
$stubDir = Join-Path $PipelineDir 'vtl_synth\utils\sandhi'
if ($BranchB -eq 'copy') {
    # The stub folder already exists: copy the CONTENT of sandhi\ (note '\*').
    New-Item -ItemType Directory -Force -Path $stubDir | Out-Null
    Copy-Item -Path (Join-Path $Sandbox 'sandhi\*') -Destination $stubDir -Recurse -Force
    Write-Host "-- Branch B activated by copy: stub overwritten, SANDHI_FULL = True"
} else {
    python -m pip install $Sandbox
    Write-Host "-- Branch B activated by pip install (hook resolves via site-packages)"
}

# --- 5) verify --------------------------------------------------------------------
Write-Host "-- running the standalone package test suite (expect: 38 passed)"
Push-Location $Sandbox
try {
    python -m pytest tests/ -q
    if ($LASTEXITCODE -ne 0) { throw "pytest failed (exit $LASTEXITCODE)" }
} finally {
    Pop-Location
}

Write-Host @"

== smoke tests (require the pipeline installed above) ==
  vtl-synth run "faut il"    -l fr --sandhi standard --no-video -o out   # fo.til
  vtl-synth run "far away"   -l en --sandhi standard --no-video -o out   # fa.R@.we
  vtl-synth run "los amigos" -l es --sandhi standard --no-video -o out   # lo.sa.mi.gos
  vtl-synth run "os amigos"  -l pt --sandhi standard --no-video -o out   # o.Z@.mi.guS
  vtl-synth run "a casa"     -l it --sandhi standard --no-video -o out   # a.kka.sa
  vtl-synth run "ein Apfel"  -l de --sandhi standard --no-video -o out   # ajn a.pf@l
== done ==
"@
