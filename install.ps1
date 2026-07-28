$ErrorActionPreference = "Stop"
Write-Host "❄️ Installing Snowline Agent Tools..." -ForegroundColor Cyan

# Install package
pip install -e .

# Get Python Scripts path
$pythonScriptsPath = (python -c "import os, sysconfig; print(sysconfig.get_path('scripts'))")
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Check and update PATH if necessary
if ($currentPath -notmatch [regex]::Escape($pythonScriptsPath)) {
    Write-Host "⚠️ Python Scripts folder is not in your PATH: $pythonScriptsPath" -ForegroundColor Yellow
    Write-Host "🔧 Adding it to User PATH automatically..." -ForegroundColor Cyan
    $newPath = "$pythonScriptsPath;" + $currentPath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "✅ PATH updated successfully! IMPORTANT: You must restart your terminal to use the 'snowline' command." -ForegroundColor Green
} else {
    Write-Host "✅ Python Scripts directory is already in PATH." -ForegroundColor Green
}
Write-Host "Installation complete! Run 'snowline -h' after restarting your terminal." -ForegroundColor Green
