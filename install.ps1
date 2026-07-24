Write-Host "[INIT] Installing 12-Pillars Agent Ecosystem (Project-Level)..." -ForegroundColor Cyan

$ProjectRoot = (Get-Location).Path
$AgentsDir = Join-Path $ProjectRoot ".agents"
$SkillsDir = Join-Path $AgentsDir "skills"
$KnowledgeDir = Join-Path $AgentsDir "knowledge"
$RepoUrl = "https://github.com/UsmanAzizz/snowline-agent-tools.git"

# Ensure .agents and .agents/knowledge exist
if (-not (Test-Path $AgentsDir)) {
    New-Item -ItemType Directory -Force -Path $AgentsDir | Out-Null
}
if (-not (Test-Path $KnowledgeDir)) {
    New-Item -ItemType Directory -Force -Path $KnowledgeDir | Out-Null
}

# Scaffold skills
if (Test-Path $SkillsDir) {
    Write-Host "[INFO] Found existing skills directory at $SkillsDir" -ForegroundColor Yellow
    if (Test-Path (Join-Path $SkillsDir ".git")) {
        Write-Host "[UPDATE] Pulling latest updates..." -ForegroundColor Cyan
        Set-Location $SkillsDir
        try {
            git pull origin main
        } catch {
            Write-Host "[ERROR] Failed to update repository." -ForegroundColor Red
        }
        Set-Location $ProjectRoot
    } else {
        Write-Host "[WARN] Existing skills directory is not a git repository. Skipping git pull." -ForegroundColor Yellow
    }
} else {
    Write-Host "[DOWNLOAD] Downloading 12-Pillars skills..." -ForegroundColor Cyan
    try {
        git clone $RepoUrl $SkillsDir
    } catch {
        Write-Host "[ERROR] Failed to clone repository. Make sure git is installed." -ForegroundColor Red
        exit 1
    }
}

# Copy AGENTS_TEMPLATE.md to AGENTS.md
$TemplatePath = Join-Path $SkillsDir "AGENTS_TEMPLATE.md"
$LocalAgentsPath = Join-Path $AgentsDir "AGENTS.md"

if (Test-Path $TemplatePath) {
    if (-not (Test-Path $LocalAgentsPath)) {
        Write-Host "[CREATE] Creating Project AGENTS.md..." -ForegroundColor Cyan
        Copy-Item -Path $TemplatePath -Destination $LocalAgentsPath -Force
        Write-Host "[SUCCESS] Project AGENTS.md created successfully." -ForegroundColor Green
    } else {
        Write-Host "[INFO] Project AGENTS.md already exists. Skipping overwrite." -ForegroundColor Yellow
    }
}

# Scaffold PLAN.md
$PlanPath = Join-Path $ProjectRoot "PLAN.md"
if (-not (Test-Path $PlanPath)) {
    Write-Host "[CREATE] Creating PLAN.md..." -ForegroundColor Cyan
    Set-Content -Path $PlanPath -Value "# Project Plan / Task Tracker`n`n- [ ] Initial task" -Encoding UTF8
}

Write-Host "`n[DONE] Installation Complete!" -ForegroundColor Green
Write-Host "This project is now powered by the 12-Pillars Ecosystem." -ForegroundColor Cyan
