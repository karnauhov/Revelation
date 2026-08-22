param(
    [string]$OutputDirectory = '',
    [string]$PublicKeyPath = "$env:USERPROFILE\.ssh\id_ed25519.pub",
    [string]$PrivateKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
    $OutputDirectory = Join-Path $desktop 'Revelation-stage7-remote-setup'
}
foreach ($keyPath in @($PublicKeyPath, $PrivateKeyPath)) {
    if (-not (Test-Path -LiteralPath $keyPath -PathType Leaf)) {
        throw "SSH key file is missing: $keyPath. Create an ed25519 key first with ssh-keygen."
    }
}
$publicKey = (Get-Content -Raw -Encoding UTF8 -LiteralPath $PublicKeyPath).Trim()
if ($publicKey -notmatch '^ssh-ed25519\s+[A-Za-z0-9+/=]+(?:\s+.*)?$') {
    throw 'PublicKeyPath must contain exactly one ssh-ed25519 public key.'
}

$sourceRoot = Split-Path -Parent $PSCommandPath
$files = @(
    'setup_stage7_remote_llm_host.ps1',
    'stage7_remote_llm_host_service.ps1',
    'stage7_remote_llm_task.ps1',
    'stage7_remote_llm_models.json'
)
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$outputRoot = (Resolve-Path -LiteralPath $OutputDirectory).Path
foreach ($name in $files) {
    $source = Join-Path $sourceRoot $name
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Remote setup source file is missing: $source"
    }
    Copy-Item -LiteralPath $source -Destination (Join-Path $outputRoot $name) -Force
}
$publicKeyDestination = Join-Path $outputRoot 'revelation_stage7_ed25519.pub'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($publicKeyDestination, $publicKey + "`n", $utf8NoBom)

$readmeBase64 = 'IyDQo9GB0YLQsNC90L7QstC60LAg0YPQtNCw0LvRkdC90L3QvtCz0L4gTExNLdGD0LfQu9CwINGN0YLQsNC/0LAgNwoKMS4g0J/QtdGA0LXQvdC10YHQuNGC0LUg0LLRgdGOINGN0YLRgyDQv9Cw0L/QutGDINC90LAg0LjQs9GA0L7QstC+0Lkg0LrQvtC80L/RjNGO0YLQtdGALgoyLiDQntGC0LrRgNC+0LnRgtC1IFBvd2VyU2hlbGwgKirQvtGCINC40LzQtdC90Lgg0LDQtNC80LjQvdC40YHRgtGA0LDRgtC+0YDQsCoqLgozLiDQn9C10YDQtdC50LTQuNGC0LUg0LIg0L/QtdGA0LXQvdC10YHRkdC90L3Rg9GOINC/0LDQv9C60YMg0Lgg0LLRi9C/0L7Qu9C90LjRgtC1OgoKICAgcG93ZXJzaGVsbCAtTm9Qcm9maWxlIC1FeGVjdXRpb25Qb2xpY3kgQnlwYXNzIC1GaWxlIC5cc2V0dXBfc3RhZ2U3X3JlbW90ZV9sbG1faG9zdC5wczEKCtCh0LrRgNC40L/RgiDRg9GB0YLQsNC90L7QstC40YIgT3BlblNTSCBTZXJ2ZXIsINGC0L7Rh9C90YvQuSBDVURBIHJ1bnRpbWUgbGxhbWEuY3BwINC4INGC0YDQuCDQv9C40LvQvtGC0L3Ri9C1INC80L7QtNC10LvQuArQvdCwIEQ6XFJldmVsYXRpb25TdGFnZTdMTE0uINCt0YLQviDQvtC60L7Qu9C+IDMwIEdCINC30LDQs9GA0YPQt9C+0LouINCc0L7QtNC10LvQuCDQvdC1INC30LDQv9C40YHRi9Cy0LDRjtGC0YHRjyDQvdCwINC/0L7Rh9GC0LgK0LfQsNC/0L7Qu9C90LXQvdC90YvQuSDQtNC40YHQuiBDOi4g0J/QvtGB0LvQtSDRg9GB0YLQsNC90L7QstC60Lgg0YHQtdGA0LLQtdGAINC+0YHRgtCw0ZHRgtGB0Y8g0LLRi9C60LvRjtGH0LXQvdC90YvQvC4KCtCf0YDQuNCy0LDRgtC90L7Qs9C+IFNTSC3QutC70Y7Rh9CwINCyINC/0LDQutC10YLQtSDQvdC10YI7INC/0LXRgNC10L3QtdGB0ZHQvSDRgtC+0LvRjNC60L4g0L/Rg9Cx0LvQuNGH0L3Ri9C5INC60LvRjtGHINCy0LvQsNC00LXQu9GM0YbQsC4K0J/QvtGB0LvQtSDQt9Cw0LLQtdGA0YjQtdC90LjRjyDQstC10YDQvdC40YLQtdGB0Ywg0Log0L3QvtGD0YLQsdGD0LrRgyDQuCDQuNGB0L/QvtC70YzQt9GD0LnRgtC1IHZlcnNpb25lZCBjb250cm9sbGVyINC40Lcg0L/RgNC+0LXQutGC0LAuCg=='
$readme = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($readmeBase64))
[IO.File]::WriteAllText((Join-Path $outputRoot 'README.ru.md'), $readme.TrimEnd() + "`n", $utf8NoBom)

$manifestFiles = @()
foreach ($path in Get-ChildItem -LiteralPath $outputRoot -File |
        Where-Object Name -ne 'package_manifest.json' |
        Sort-Object Name) {
    $manifestFiles += [ordered]@{
        filename = $path.Name
        size_bytes = [uint64]$path.Length
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path.FullName).Hash.ToLowerInvariant()
    }
}
$manifest = [ordered]@{
    schema_version = 1
    package_version = 'ukrainian-stage-7-remote-llm-setup-v1'
    status = 'complete_flash_transfer_package'
    contains_private_key = $false
    owner_private_key_present_on_laptop = $true
    target_host = 'COMP_NAZARA'
    target_host_ipv4 = '192.168.1.188'
    owner_laptop_ipv4 = '192.168.1.251'
    files = $manifestFiles
    processed_count = $manifestFiles.Count
    skipped_count = 0
    error_count = 0
}
$manifestPath = Join-Path $outputRoot 'package_manifest.json'
[IO.File]::WriteAllText($manifestPath, (($manifest | ConvertTo-Json -Depth 8) + "`n"), $utf8NoBom)

Write-Host "Flash package ready: $outputRoot"
Write-Host 'Copy the whole directory to the gaming computer; it contains no private SSH key.'
