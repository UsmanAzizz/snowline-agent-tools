$source = "src\snowline\templates\skills"
$target = "..\cbt_master\.agents\skills"

# Get hashes for all files excluding .history and __pycache__
$sourceHashes = Get-ChildItem -Path $source -Recurse -File | Where-Object { $_.FullName -notmatch '\.history' -and $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' } | Get-FileHash
$targetHashes = Get-ChildItem -Path $target -Recurse -File | Where-Object { $_.FullName -notmatch '\.history' -and $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' } | Get-FileHash

# Create dictionaries mapping relative paths to hashes
$sourceDict = @{}
foreach ($item in $sourceHashes) {
    $relPath = $item.Path.Substring((Resolve-Path $source).Path.Length + 1)
    $sourceDict[$relPath] = $item.Hash
}

$targetDict = @{}
foreach ($item in $targetHashes) {
    $relPath = $item.Path.Substring((Resolve-Path $target).Path.Length + 1)
    $targetDict[$relPath] = $item.Hash
}

$target2 = ".agents\skills"
$target2Hashes = Get-ChildItem -Path $target2 -Recurse -File | Where-Object { $_.FullName -notmatch '\.history' -and $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' } | Get-FileHash
$target2Dict = @{}
foreach ($item in $target2Hashes) {
    $relPath = $item.Path.Substring((Resolve-Path $target2).Path.Length + 1)
    $target2Dict[$relPath] = $item.Hash
}

$sama1 = 0
$beda1 = 0
$hilangS1 = 0
$hilangT1 = 0

$sama2 = 0
$beda2 = 0
$hilangS2 = 0
$hilangT2 = 0

$allKeys1 = $sourceDict.Keys + $targetDict.Keys | Sort-Object -Unique
$allKeys2 = $sourceDict.Keys + $target2Dict.Keys | Sort-Object -Unique

foreach ($key in $allKeys1) {
    if (-not $sourceDict.ContainsKey($key)) { $hilangS1++ }
    elseif (-not $targetDict.ContainsKey($key)) { $hilangT1++ }
    elseif ($sourceDict[$key] -ne $targetDict[$key]) { $beda1++ }
    else { $sama1++ }
}

foreach ($key in $allKeys2) {
    if (-not $sourceDict.ContainsKey($key)) { $hilangS2++ }
    elseif (-not $target2Dict.ContainsKey($key)) { $hilangT2++ }
    elseif ($sourceDict[$key] -ne $target2Dict[$key]) { $beda2++ }
    else { $sama2++ }
}

Write-Host "TARGET 1 (cbt_master): sama = $sama1    beda = $beda1    hilang_sumber = $hilangS1    hilang_turunan = $hilangT1"
Write-Host "TARGET 2 (dogfooding): sama = $sama2    beda = $beda2    hilang_sumber = $hilangS2    hilang_turunan = $hilangT2"

if ($beda1 -gt 0 -or $hilangS1 -gt 0 -or $hilangT1 -gt 0 -or $beda2 -gt 0 -or $hilangS2 -gt 0 -or $hilangT2 -gt 0) {
    exit 1
} else {
    exit 0
}
