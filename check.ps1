$ErrorActionPreference = "Continue"

# ============================================================
# IdentityAI - Fix + Full Health Check
# ============================================================

if ($PSScriptRoot) {
    $ROOT = $PSScriptRoot
}
else {
    $ROOT = (Get-Location).Path
}

$FRONTEND = Join-Path $ROOT "frontend"
$PYTHON = Join-Path $ROOT "env\Scripts\python.exe"
$REGISTER_PAGE = Join-Path $FRONTEND "pages\register.tsx"
$PROVER = Join-Path $ROOT "docs\prover.js"
$SMOKE_TEST = Join-Path $ROOT "smoke-test.py"
$CHECK_SCRIPT = Join-Path $ROOT "check.ps1"

$PASS = 0
$FAIL = 0
$WARN = 0

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

function Run-Command {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    $output = & $Command @Arguments 2>&1
    $exitCode = $LASTEXITCODE

    return @{
        Output = $output
        ExitCode = $exitCode
    }
}


# ============================================================
# Environment
# ============================================================

Header "IdentityAI Fix + Health Check"

Write-Host "Project root: $ROOT" -ForegroundColor DarkGray

if (-not (Test-Path $PYTHON)) {
    Fail "Python virtual environment not found: $PYTHON"
    exit 1
}

Pass "Python virtual environment found"

if (-not (Test-Path $FRONTEND)) {
    Fail "Frontend directory not found: $FRONTEND"
    exit 1
}

Pass "Frontend directory found"


# ============================================================
# 1. Backend environment
# ============================================================

Header "Backend Environment"

Push-Location $ROOT

$pythonVersion = & $PYTHON --version 2>&1
Write-Host $pythonVersion

$envFile = Join-Path $ROOT ".env"

if (Test-Path $envFile) {
    Pass ".env exists"
}
else {
    Warn ".env not found"
}

# ============================================================
# 2. Django checks
# ============================================================

Header "Django Checks"

$result = Run-Command $PYTHON @("manage.py", "check")

$result.Output | ForEach-Object {
    Write-Host $_
}

if ($result.ExitCode -eq 0) {
    Pass "Django system check"
}
else {
    Fail "Django system check"
}


# ============================================================
# 3. Django migrations
# ============================================================

Header "Django Migrations"

$migrationResult = Run-Command $PYTHON @(
    "manage.py",
    "makemigrations",
    "--check"
)

$migrationResult.Output | ForEach-Object {
    Write-Host $_
}

if ($migrationResult.ExitCode -eq 0) {
    Pass "No missing Django migrations"
}
else {
    Warn "Django reports missing migration changes"
}


# ============================================================
# 4. Django tests
# ============================================================

Header "Django Tests"

$testResult = Run-Command $PYTHON @(
    "manage.py",
    "test"
)

$testResult.Output | ForEach-Object {
    Write-Host $_
}

if ($testResult.ExitCode -eq 0) {
    Pass "Django test suite"
}
else {
    Fail "Django test suite"
}


# ============================================================
# 5. Deployment warnings
# ============================================================

Header "Django Deployment Check"

$deployResult = Run-Command $PYTHON @(
    "manage.py",
    "check",
    "--deploy"
)

$deployText = ($deployResult.Output -join "`n")

$deployResult.Output | ForEach-Object {
    Write-Host $_ -ForegroundColor DarkYellow
}

if ($deployResult.ExitCode -ne 0) {
    Fail "Django deployment check failed"
}
elseif ($deployText -match "WARNINGS:" -or $deployText -match "Found \d+ issue") {
    Warn "Django deployment check has production warnings"
}
else {
    Pass "Django deployment check"
}


# ============================================================
# 6. Frontend dependencies
# ============================================================

Header "Frontend Dependencies"

Push-Location $FRONTEND

if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules missing. Running npm install..." -ForegroundColor Yellow

    npm install

    if ($LASTEXITCODE -eq 0) {
        Pass "npm install"
    }
    else {
        Fail "npm install"
    }
}
else {
    Pass "Frontend dependencies available"
}


# ============================================================
# 7. Safe frontend lint fix
# ============================================================

Header "Frontend Safe Fixes"

if (Test-Path $REGISTER_PAGE) {

    $content = Get-Content $REGISTER_PAGE -Raw

    # Fix only the known ESLint react/no-unescaped-entities
    # issue caused by literal apostrophes in JSX text.
    $updated = $content `
        -replace "We couldn't", "We couldn&apos;t" `
        -replace "We're", "We&apos;re"

    if ($updated -ne $content) {

        Set-Content `
            -Path $REGISTER_PAGE `
            -Value $updated `
            -Encoding UTF8

        Pass "Fixed known JSX apostrophe lint issue in register.tsx"
    }
    else {
        Pass "No known JSX apostrophe fix required"
    }

}
else {
    Warn "register.tsx not found"
}


# ============================================================
# 8. Check package scripts
# ============================================================

$packageJson = Join-Path $FRONTEND "package.json"

if (Test-Path $packageJson) {

    $package = Get-Content $packageJson -Raw | ConvertFrom-Json

    if ($package.scripts.lint) {
        Pass "Frontend lint script exists"
    }
    else {
        Fail "Frontend lint script missing"
    }

    if ($package.scripts.build) {
        Pass "Frontend build script exists"
    }
    else {
        Fail "Frontend build script missing"
    }

}
else {
    Fail "frontend/package.json not found"
}


# ============================================================
# 9. Frontend lint
# ============================================================

Header "Frontend Lint"

$lintResult = Run-Command "npm" @("run", "lint")

$lintResult.Output | ForEach-Object {
    Write-Host $_
}

if ($lintResult.ExitCode -eq 0) {
    Pass "Frontend lint"
}
else {
    Fail "Frontend lint"
}


# ============================================================
# 10. Frontend build
# ============================================================

Header "Frontend Build"

$buildResult = Run-Command "npm" @("run", "build")

$buildResult.Output | ForEach-Object {
    Write-Host $_
}

if ($buildResult.ExitCode -eq 0) {
    Pass "Frontend production build"
}
else {
    Fail "Frontend production build"
}

Pop-Location


# ============================================================
# 11. ZKP environment inspection
# ============================================================

Header "V0.4 ZKP Environment"

if (-not (Test-Path $PROVER)) {
    Fail "docs/prover.js not found"
}
else {
    Pass "ZKP prover found"
}

$circuits = Get-ChildItem `
    -Path $ROOT `
    -Recurse `
    -Include *.circom `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "node_modules|\.next"
    }

if ($circuits.Count -gt 0) {
    Pass "Circom circuit found"
}
else {
    Warn "No .circom circuit found"
}

$zkeys = Get-ChildItem `
    -Path $ROOT `
    -Recurse `
    -Include *.zkey `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "node_modules|\.next"
    }

if ($zkeys.Count -gt 0) {
    Pass "ZKey found"
}
else {
    Warn "No ZKey found"
}


# ============================================================
# 12. ZKP tool versions
# ============================================================

$nodeVersion = node --version 2>&1
$npmVersion = npm --version 2>&1

Write-Host "Node: $nodeVersion"
Write-Host "npm : $npmVersion"

# Prefer direct snarkjs binary if available, otherwise try npx. Validate output contains a semver-like string.
$snarkResult = Run-Command "snarkjs" @("--version")
$snarkOutput = $snarkResult.Output -join " `n "
if ($snarkResult.ExitCode -ne 0 -or -not ($snarkOutput -match "\d+\.\d+\.\d+")) {
    Write-Host "snarkjs (direct) not usable, trying npx..."
    $snarkResult = Run-Command "npx" @("snarkjs", "--version")
    $snarkOutput = $snarkResult.Output -join " `n "
}

$snarkOutput | ForEach-Object { Write-Host $_ }

if ($snarkResult.ExitCode -eq 0 -and ($snarkOutput -match "\d+\.\d+\.\d+")) {
    Pass "snarkjs available"
} else {
    Fail "snarkjs unavailable"
}


# ============================================================
# 13. Run prover directly
# ============================================================

Header "Direct ZKP Prover Test"

if (Test-Path $PROVER) {

    Write-Host "Running:" -ForegroundColor DarkGray
    Write-Host "node $PROVER" -ForegroundColor DarkGray

    $proverOutput = & node $PROVER 2>&1
    $proverExit = $LASTEXITCODE

    $proverOutput | ForEach-Object {
        Write-Host $_
    }

    if ($proverExit -eq 0) {
        Pass "Direct prover execution"
    }
    else {
        Fail "Direct prover execution"
        Write-Host "Prover exit code: $proverExit" -ForegroundColor Red
    }

}
else {
    Fail "Cannot run prover because docs/prover.js does not exist"
}


# ============================================================
# 14. Backend smoke test
# ============================================================

Header "Backend Smoke Test"

if (Test-Path $SMOKE_TEST) {

    $smokeResult = Run-Command $PYTHON @(
        $SMOKE_TEST
    )

    $smokeResult.Output | ForEach-Object {
        Write-Host $_
    }

    if ($smokeResult.ExitCode -eq 0) {
        Pass "Core backend smoke test"
    }
    else {
        Fail "Core backend smoke test"
    }

}
else {
    Warn "smoke-test.py not found"
}


# ============================================================
# 15. Final summary
# ============================================================

Pop-Location

Header "RESULT"

Write-Host "Passed : $PASS" -ForegroundColor Green
Write-Host "Failed : $FAIL" -ForegroundColor Red
Write-Host "Warned : $WARN" -ForegroundColor Yellow
Write-Host ""

if ($FAIL -eq 0) {

    Write-Host "IDENTITYAI CHECK PASSED" -ForegroundColor Green
    Write-Host ""

    Write-Host "Core system is healthy." -ForegroundColor Green

    exit 0
}

Write-Host "IDENTITYAI CHECK FAILED" -ForegroundColor Red
Write-Host ""

Write-Host "Fix the failures above before committing." -ForegroundColor Yellow

exit 1
