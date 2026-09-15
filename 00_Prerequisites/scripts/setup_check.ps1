# Verify the prerequisites for the AI FDE Certification.
#
# Read-only: this reports, it does not install or change anything. Every failure
# points at the guide that fixes it.
#
#   .\00_Prerequisites\scripts\setup_check.ps1
#
# If PowerShell refuses to run this, it is the execution policy, not the script:
#   powershell -ExecutionPolicy Bypass -File .\00_Prerequisites\scripts\setup_check.ps1

$script:Pass = 0
$script:Warn = 0
$script:Fail = 0

function Write-Ok   ($m)     { Write-Host "  " -NoNewline; Write-Host "OK  " -ForegroundColor Green -NoNewline; Write-Host $m; $script:Pass++ }
function Write-Warn ($m, $h) { Write-Host "  " -NoNewline; Write-Host "!   " -ForegroundColor Yellow -NoNewline; Write-Host $m; Write-Host "        $h" -ForegroundColor DarkGray; $script:Warn++ }
function Write-Bad  ($m, $h) { Write-Host "  " -NoNewline; Write-Host "X   " -ForegroundColor Red -NoNewline; Write-Host $m; Write-Host "        $h" -ForegroundColor DarkGray; $script:Fail++ }
function Write-Head ($m)     { Write-Host ""; Write-Host $m }

function Get-Ver ($exe) {
    try { (& $exe --version 2>$null | Select-Object -First 1) } catch { "" }
}

Write-Head "Tooling  (guide 1)"

foreach ($t in @("git", "docker", "python", "uv")) {
    if (Get-Command $t -ErrorAction SilentlyContinue) {
        Write-Ok "$t  $(Get-Ver $t)"
    }
    elseif ($t -eq "docker" -and (Get-Command podman -ErrorAction SilentlyContinue)) {
        Write-Warn "docker not found, but podman is" `
                   "Podman works for this course. Note which one in use_case/ecosystem.md."
    }
    else {
        Write-Bad "$t not found" "See 00_Prerequisites/1_Your_Machine/README.md"
    }
}

# Python version, not just presence. A bare 'python' on Windows is often the
# Store stub, which exits 9009 rather than printing a version.
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pv = & python -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
    if ($LASTEXITCODE -eq 0 -and $pv) {
        $parts = $pv.Split(".")
        if ([int]$parts[0] -gt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 12)) {
            Write-Ok "python is 3.12+  ($pv)"
        } else {
            Write-Bad "python is older than 3.12  ($pv)" "Install 3.12+; see guide 1"
        }
    } else {
        Write-Bad "python did not run" `
                  "This is usually the Microsoft Store stub. Install from python.org and tick 'Add python.exe to PATH'."
    }
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
    & docker info *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "docker daemon is running"
    } else {
        Write-Warn "docker is installed but the daemon is not responding" `
                   "Start Docker Desktop before Week 1's Step 5."
    }
}

Write-Head "Claude Code  (guide 2)"

if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-Ok "claude  $(Get-Ver claude)"
    Write-Host "        run 'claude doctor' for full diagnostics" -ForegroundColor DarkGray
} else {
    Write-Bad "claude not found" "See 00_Prerequisites/2_Claude_Code/README.md"
}

Write-Head "Repository  (guide 3)"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $Root

& git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Ok "inside a git repository"
    $origin = (& git remote get-url origin 2>$null)
    if (-not $origin) {
        Write-Warn "no 'origin' remote" "Clone your fork rather than downloading a zip."
    }
    elseif ($origin -match "AI-Maker-Space/The-AI-Forward-Deployed-Engineer-Certification") {
        Write-Warn "origin is the upstream repository, not your fork" `
                   "Fork it and clone your fork -- you need somewhere to commit your work."
    }
    else {
        Write-Ok "origin is your own fork  $origin"
    }
} else {
    Write-Bad "not a git repository" "Clone your fork; see guide 3"
}

Write-Head "Model configuration  (guide 4)"

$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    Write-Ok ".env exists at the repo root"
    $lines = Get-Content $EnvFile
    $model = ($lines | Where-Object { $_ -match '^\s*LLM_MODEL=' } | Select-Object -Last 1)
    if ($model) {
        Write-Ok "LLM_MODEL = $(($model -split '=', 2)[1].Trim(@('"', "'")))"
    } else {
        Write-Bad "LLM_MODEL is not set in .env" "See 00_Prerequisites/4_Your_Model/README.md"
    }
    if ($lines | Where-Object { $_ -match '^\s*OPENAI_API_KEY=sk-\.\.\.\s*$' }) {
        Write-Bad "OPENAI_API_KEY is still the placeholder from the template" `
                  "Paste a real key, or switch to an endpoint/local model."
    }
} else {
    Write-Bad ".env not found at the repo root" "copy .env.template .env, then fill it in"
}

$ChallengeEnv = Join-Path $Root "01_Product_Engineering\challenge\enterprise_fde_challenge\.env"
if (Test-Path $ChallengeEnv) {
    Write-Ok "the Week 1 challenge has its own .env"
} else {
    Write-Warn "the Week 1 challenge has no .env yet" `
               "copy .env.example .env inside enterprise_fde_challenge\ -- it is a separate file."
}

Write-Head "Result"
Write-Host "  $script:Pass passed" -ForegroundColor Green -NoNewline
Write-Host "   $script:Warn warning(s)" -ForegroundColor Yellow -NoNewline
Write-Host "   $script:Fail failure(s)" -ForegroundColor Red
Write-Host ""

if ($script:Fail -gt 0) {
    Write-Host "  Fix the X items before Session 1. Each one names the guide that covers it."
    Write-Host ""
    Write-Host "  If something is blocked by policy rather than broken, that is a finding,"
    Write-Host "  not a failure -- write it in use_case/ecosystem.md and carry on. Week 9"
    Write-Host "  needs it."
    Write-Host ""
    exit 1
}

if ($script:Warn -gt 0) { Write-Host "  Warnings are not blockers, but read them."; Write-Host "" }
Write-Host "  Ready for Session 1."
Write-Host ""
