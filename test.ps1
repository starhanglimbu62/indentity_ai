$ErrorActionPreference = "Continue"

# ============================================================
# IdentityAI - Final Test Runner
#
# Purpose:
#   Read-only project validation.
#
# It DOES:
#   - Check environment
#   - Check Django
#   - Check migrations
#   - Run Django tests
#   - Run deployment checks
#   - Run backend smoke test
#   - Check frontend dependencies
#   - Run frontend lint
#   - Run frontend production build
#   - Inspect ZKP artifacts
#   - Check snarkjs availability
#   - Run the real ZKP prover with timeout
#
# It DOES NOT:
#   - Modify source files
#   - Modify package.json
#   - Install dependencies
#   - Change TypeScript versions
#   - Modify the ZKP circuit
#   - Modify the prover
# ============================================================


# ============================================================
# Resolve project root
# ============================================================

if ($PSScriptRoot) {
    $ROOT = $PSScriptRoot
}
else {
    $ROOT = (Get-Location).Path
}

$FRONTEND = Join-Path $ROOT "frontend"
$PYTHON = Join-Path $ROOT "env\Scripts\python.exe"
$SMOKE_TEST = Join-Path $ROOT "smoke-test.py"
$PROVER = Join-Path $ROOT "docs\prover.js"

$PASS = 0
$FAIL = 0
$WARN = 0


# ============================================================
# Output helpers
# ============================================================

function Header([string]$Text) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Pass([string]$Text) {
    $script:PASS++
    Write-Host "[PASS] $Text" -ForegroundColor Green
}

function Fail([string]$Text) {
    $script:FAIL++
    Write-Host "[FAIL] $Text" -ForegroundColor Red
}

function Warn([string]$Text) {
    $script:WARN++
    Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

function Run-External {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    $Output = & $Command @Arguments 2>&1
    $ExitCode = $LASTEXITCODE

    return @{
        Output   = $Output
        ExitCode = $ExitCode
    }
}


# ============================================================
# Header
# ============================================================

Header "IdentityAI Final Test Suite"

Write-Host "Project root: $ROOT" -ForegroundColor DarkGray


# ============================================================
# 1. Environment
# ============================================================

Header "1. Environment"

if (Test-Path $PYTHON) {
    Pass "Python virtual environment found"
}
else {
    Fail "Python virtual environment not found: $PYTHON"
}

if (Test-Path $FRONTEND) {
    Pass "Frontend directory found"
}
else {
    Fail "Frontend directory not found: $FRONTEND"
}

if (-not (Test-Path $PYTHON)) {
    Write-Host ""
    Write-Host "Cannot continue without Python." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $FRONTEND)) {
    Write-Host ""
    Write-Host "Cannot continue without frontend." -ForegroundColor Red
    exit 1
}


# ============================================================
# 2. Python version
# ============================================================

Header "2. Python"

$PythonVersion = & $PYTHON --version 2>&1

Write-Host $PythonVersion

Pass "Python executable available"


# ============================================================
# 3. Django system check
# ============================================================

Header "3. Django System Check"

Push-Location $ROOT

$Result = Run-External $PYTHON @(
    "manage.py",
    "check"
)

$Result.Output | ForEach-Object {
    Write-Host $_
}

if ($Result.ExitCode -eq 0) {
    Pass "python manage.py check"
}
else {
    Fail "python manage.py check"
}


# ============================================================
# 4. Migration check
# ============================================================

Header "4. Django Migration Check"

$Result = Run-External $PYTHON @(
    "manage.py",
    "makemigrations",
    "--check"
)

$Result.Output | ForEach-Object {
    Write-Host $_
}

if ($Result.ExitCode -eq 0) {
    Pass "No missing migrations"
}
else {
    Fail "Missing migration changes detected"
}


# ============================================================
# 5. Django test suite
# ============================================================

Header "5. Django Tests"

$Result = Run-External $PYTHON @(
    "manage.py",
    "test"
)

$Result.Output | ForEach-Object {
    Write-Host $_
}

if ($Result.ExitCode -eq 0) {
    Pass "Django test suite"
}
else {
    Fail "Django test suite"
}


# ============================================================
# 6. Django deployment check
# ============================================================

Header "6. Django Deployment Check"

$Result = Run-External $PYTHON @(
    "manage.py",
    "check",
    "--deploy"
)

$DeployText = $Result.Output -join "`n"

$Result.Output | ForEach-Object {
    Write-Host $_ -ForegroundColor DarkYellow
}

if ($Result.ExitCode -ne 0) {
    Fail "Django deployment check failed"
}
elseif (
    $DeployText -match "WARNINGS:" -or
    $DeployText -match "Found \d+ issue"
) {
    Warn "Django deployment check contains production warnings"
}
else {
    Pass "Django deployment check"
}


# ============================================================
# 7. Backend smoke test
# ============================================================

Header "7. Backend Smoke Test"

if (-not (Test-Path $SMOKE_TEST)) {

    Warn "smoke-test.py not found"

}
else {

    $Result = Run-External $PYTHON @(
        $SMOKE_TEST
    )

    $Result.Output | ForEach-Object {
        Write-Host $_
    }

    if ($Result.ExitCode -eq 0) {
        Pass "Backend smoke test"
    }
    else {
        Fail "Backend smoke test"
    }
}


# ============================================================
# 8. Frontend package validation
# ============================================================

Header "8. Frontend"

Push-Location $FRONTEND

if (Test-Path "package.json") {
    Pass "package.json found"
}
else {
    Fail "package.json not found"
}

if (Test-Path "node_modules") {
    Pass "node_modules found"
}
else {
    Fail "node_modules not found"
}


# ============================================================
# 9. Frontend package scripts
# ============================================================

Header "9. Frontend Scripts"

if (Test-Path "package.json") {

    try {

        $Package = Get-Content "package.json" -Raw |
            ConvertFrom-Json

        if ($Package.scripts.dev) {
            Pass "npm run dev exists"
        }
        else {
            Fail "npm run dev missing"
        }

        if ($Package.scripts.lint) {
            Pass "npm run lint exists"
        }
        else {
            Fail "npm run lint missing"
        }

        if ($Package.scripts.build) {
            Pass "npm run build exists"
        }
        else {
            Fail "npm run build missing"
        }

    }
    catch {

        Fail "Unable to parse frontend/package.json"
    }
}


# ============================================================
# 10. Node / Next.js
# ============================================================

Header "10. Node / Next.js"

$NodeVersion = node --version 2>&1
$NpmVersion = npm --version 2>&1
$NextVersion = npx next --version 2>&1

Write-Host "Node: $NodeVersion"
Write-Host "npm : $NpmVersion"
Write-Host "Next: $NextVersion"

if ($LASTEXITCODE -eq 0) {
    Pass "Next.js available"
}
else {
    Fail "Next.js unavailable"
}


# ============================================================
# 11. Frontend lint
# ============================================================

Header "11. Frontend Lint"

$Result = Run-External "npm" @(
    "run",
    "lint"
)

$Result.Output | ForEach-Object {
    Write-Host $_
}

if ($Result.ExitCode -eq 0) {
    Pass "npm run lint"
}
else {
    Fail "npm run lint"
}


# ============================================================
# 12. Frontend build
# ============================================================

Header "12. Frontend Build"

$Result = Run-External "npm" @(
    "run",
    "build"
)

$Result.Output | ForEach-Object {
    Write-Host $_
}

if ($Result.ExitCode -eq 0) {
    Pass "npm run build"
}
else {
    Fail "npm run build"
}


# ============================================================
# Leave frontend directory
# ============================================================

Pop-Location


# ============================================================
# 13. ZKP environment
# ============================================================

Header "13. V0.4 ZKP Environment"

if (Test-Path $PROVER) {
    Pass "docs/prover.js found"
}
else {
    Fail "docs/prover.js not found"
}


# ------------------------------------------------------------
# Circom
# ------------------------------------------------------------

$Circuits = Get-ChildItem `
    -Path $ROOT `
    -Recurse `
    -Filter "*.circom" `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "node_modules|\.next"
    }

if ($Circuits.Count -gt 0) {
    Pass "Circom circuit found"

    foreach ($Circuit in $Circuits) {
        Write-Host "  $($Circuit.FullName)" -ForegroundColor DarkGray
    }
}
else {
    Warn "No .circom circuit found"
}


# ------------------------------------------------------------
# ZKey
# ------------------------------------------------------------

$ZKeys = Get-ChildItem `
    -Path $ROOT `
    -Recurse `
    -Filter "*.zkey" `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "node_modules|\.next"
    }

if ($ZKeys.Count -gt 0) {
    Pass "ZKey found"

    foreach ($ZKey in $ZKeys) {
        Write-Host "  $($ZKey.FullName)" -ForegroundColor DarkGray
    }
}
else {
    Warn "No .zkey found"
}


# ============================================================
# 14. snarkjs
# ============================================================

Header "14. snarkjs"

$SnarkOutput = & npx snarkjs 2>&1
$SnarkExit = $LASTEXITCODE

$SnarkText = $SnarkOutput -join "`n"

$SnarkOutput | ForEach-Object {
    Write-Host $_
}

if (
    $SnarkExit -eq 0 -and
    $SnarkText -match "snarkjs"
) {
    Pass "snarkjs available"
}
else {
    Fail "snarkjs unavailable"
}


# ============================================================
# 15. Direct ZKP prover
# ============================================================

Header "15. Direct ZKP Prover"

if (Test-Path $PROVER) {

    $StdoutFile = Join-Path $ROOT ".prover.stdout.tmp"
    $StderrFile = Join-Path $ROOT ".prover.stderr.tmp"

    Remove-Item $StdoutFile -Force -ErrorAction SilentlyContinue
    Remove-Item $StderrFile -Force -ErrorAction SilentlyContinue

    Write-Host ""
    Write-Host "Running real prover with 120-second timeout..." -ForegroundColor Yellow
    Write-Host "node $PROVER" -ForegroundColor DarkGray
    Write-Host ""

    try {

        $Process = Start-Process `
            -FilePath "node" `
            -ArgumentList "`"$PROVER`"" `
            -WorkingDirectory $ROOT `
            -RedirectStandardOutput $StdoutFile `
            -RedirectStandardError $StderrFile `
            -PassThru `
            -NoNewWindow

        $Completed = $Process.WaitForExit(120000)

        if (-not $Completed) {

            Write-Host ""
            Write-Host "--- PROVER TIMEOUT ---" -ForegroundColor Red
            Write-Host "The prover exceeded 120 seconds." -ForegroundColor Red

            try {
                Stop-Process `
                    -Id $Process.Id `
                    -Force `
                    -ErrorAction SilentlyContinue
            }
            catch {
            }

            if (Test-Path $StdoutFile) {
                Write-Host ""
                Write-Host "--- PROVER STDOUT ---" -ForegroundColor Gray
                Get-Content $StdoutFile
            }

            if (Test-Path $StderrFile) {
                Write-Host ""
                Write-Host "--- PROVER STDERR ---" -ForegroundColor Red
                Get-Content $StderrFile
            }

            Fail "ZKP prover timed out"

        }
        else {

            if (Test-Path $StdoutFile) {
                Write-Host ""
                Write-Host "--- PROVER STDOUT ---" -ForegroundColor Gray
                Get-Content $StdoutFile
            }

            if (Test-Path $StderrFile) {
                Write-Host ""
                Write-Host "--- PROVER STDERR ---" -ForegroundColor Red
                Get-Content $StderrFile
            }

            $ExitCode = $Process.ExitCode

            if ($ExitCode -eq 0) {
                Pass "ZKP prover executed successfully"
            }
            else {
                Fail "ZKP prover failed"
                Write-Host "Exit code: $ExitCode" -ForegroundColor Red
            }
        }

    }
    catch {

        Fail "Unable to start ZKP prover"

        Write-Host $_ -ForegroundColor Red
    }

    Remove-Item $StdoutFile -Force -ErrorAction SilentlyContinue
    Remove-Item $StderrFile -Force -ErrorAction SilentlyContinue

}
else {
    Fail "Cannot test prover because docs/prover.js is missing"
}


# ============================================================
# 16. Repository status
# ============================================================

Header "16. Git Status"

Push-Location $ROOT

git status --short

Pop-Location


# ============================================================
# Final result
# ============================================================

Header "RESULT"

Write-Host "Passed : $PASS" -ForegroundColor Green
Write-Host "Failed : $FAIL" -ForegroundColor Red
Write-Host "Warned : $WARN" -ForegroundColor Yellow
Write-Host ""

if ($FAIL -eq 0) {

    Write-Host "IDENTITYAI TEST SUITE PASSED" -ForegroundColor Green
    Write-Host ""
    Write-Host "No blocking test failures detected." -ForegroundColor Green

    exit 0
}

Write-Host "IDENTITYAI TEST SUITE FAILED" -ForegroundColor Red
Write-Host ""
Write-Host "Blocking failures must be fixed before committing." -ForegroundColor Yellow

exit 1