$ErrorActionPreference = "Stop"

$sourceBase = "src\snowline\templates"
$targets = @("..\cbt_master\.agents", ".agents", "test_hook_arah6\.agents")
$itemsToCheck = @("skills", "hooks", "hooks.json")

$hasError = $false

foreach ($targetBase in $targets) {
    if (-not (Test-Path $targetBase)) {
        Write-Host "Target missing: $targetBase"
        $hasError = $true
        continue
    }

    foreach ($item in $itemsToCheck) {
        $sourcePath = Join-Path $sourceBase $item
        $targetPath = Join-Path $targetBase $item

        if (-not (Test-Path $sourcePath)) { continue }

        if (-not (Test-Path $targetPath)) {
            Write-Host "ERROR: Missing $item in $targetBase"
            $hasError = $true
            continue
        }

        function Get-NormalizedHash($path) {
            $content = [System.IO.File]::ReadAllText($path).Replace("`r`n", "`n")
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
            $hash = [System.Security.Cryptography.MD5]::Create().ComputeHash($bytes)
            return [System.BitConverter]::ToString($hash).Replace("-", "").ToLower()
        }

        # If it's a file (hooks.json)
        if ((Get-Item $sourcePath) -is [System.IO.FileInfo]) {
            $sHash = Get-NormalizedHash $sourcePath
            $tHash = Get-NormalizedHash $targetPath
            if ($sHash -ne $tHash) {
                Write-Host "ERROR: File divergence $item in $targetBase"
                $hasError = $true
            }
            continue
        }

        # If it's a directory
        $sFiles = Get-ChildItem -Path $sourcePath -Recurse -File | Where-Object { $_.FullName -notmatch '\.history' -and $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' }
        $tFiles = Get-ChildItem -Path $targetPath -Recurse -File | Where-Object { $_.FullName -notmatch '\.history' -and $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' }

        $sDict = @{}
        foreach ($f in $sFiles) {
            $rel = $f.FullName.Substring((Resolve-Path $sourcePath).Path.Length + 1)
            $sDict[$rel] = Get-NormalizedHash $f.FullName
        }

        $tDict = @{}
        foreach ($f in $tFiles) {
            $rel = $f.FullName.Substring((Resolve-Path $targetPath).Path.Length + 1)
            $tDict[$rel] = Get-NormalizedHash $f.FullName
        }

        $allKeys = $sDict.Keys + $tDict.Keys | Sort-Object -Unique
        foreach ($k in $allKeys) {
            if (-not $sDict.ContainsKey($k)) {
                Write-Host "ERROR: Extra file in target $targetBase\$item\$k"
                $hasError = $true
            } elseif (-not $tDict.ContainsKey($k)) {
                Write-Host "ERROR: Missing file in target $targetBase\$item\$k"
                $hasError = $true
            } elseif ($sDict[$k] -ne $tDict[$k]) {
                Write-Host "ERROR: Content divergence $targetBase\$item\$k"
                $hasError = $true
            }
        }
    }
}

$chamberTemplate = "src\snowline\chamber_templates\CHAMBER_RULES.md"
$chamberTarget = "agents_chamber\CHAMBER_RULES.md"
if (Test-Path $chamberTemplate) {
    if (-not (Test-Path $chamberTarget)) {
        Write-Host "ERROR: Missing CHAMBER_RULES.md in agents_chamber"
        $hasError = $true
    } else {
        $tmplHash = Get-NormalizedHash $chamberTemplate
        $tgtHash = Get-NormalizedHash $chamberTarget
        if ($tmplHash -ne $tgtHash) {
            Write-Host "ERROR: File divergence between $chamberTemplate and $chamberTarget"
            $hasError = $true
        }
    }
}

if ($hasError) {
    Write-Host "Rule #12 Violation Detected."
    exit 1
} else {
    Write-Host "Rule #12 Verified: All targets are byte-identical."
    exit 0
}
