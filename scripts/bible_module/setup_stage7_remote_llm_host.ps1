param(
    [string]$OwnerLaptopAddress = '192.168.1.251',
    [string]$ServiceRoot = 'D:\RevelationStage7LLM',
    [switch]$SkipModelDownloads
)

$ErrorActionPreference = 'Stop'
$taskName = 'RevelationStage7LlamaServer'

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList
    )
    # Windows PowerShell 5.1 can wrap redirected native stderr as a
    # NativeCommandError when ErrorActionPreference is Stop. llama.cpp writes
    # informational version/device lines to stderr, so capture them under
    # Continue and validate the real native exit code explicitly.
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $nativeLines = @(& $FilePath @ArgumentList 2>&1 | ForEach-Object { [string]$_ })
        $nativeExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($nativeExitCode -ne 0) {
        throw "Native command failed with exit code $nativeExitCode`: $FilePath $($ArgumentList -join ' ')"
    }
    return ($nativeLines -join "`n").Trim()
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this setup script from PowerShell opened as Administrator.'
}
if ($OwnerLaptopAddress -notmatch '^192\.168\.1\.\d{1,3}$') {
    throw 'OwnerLaptopAddress must be the expected private 192.168.1.x address.'
}
if (-not $ServiceRoot.StartsWith('D:\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'The remote LLM root must stay on D: because C: has insufficient free space.'
}
if (-not $ServiceRoot.Equals('D:\RevelationStage7LLM', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'This frozen pilot package supports only D:\RevelationStage7LLM.'
}

$sourceRoot = Split-Path -Parent $PSCommandPath
$sourceRegistry = Join-Path $sourceRoot 'stage7_remote_llm_models.json'
$sourceService = Join-Path $sourceRoot 'stage7_remote_llm_host_service.ps1'
$sourceTask = Join-Path $sourceRoot 'stage7_remote_llm_task.ps1'
$publicKeyPath = Join-Path $sourceRoot 'revelation_stage7_ed25519.pub'
foreach ($required in @($sourceRegistry, $sourceService, $sourceTask, $publicKeyPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Setup package is incomplete: $required"
    }
}

$registry = Get-Content -Raw -Encoding UTF8 -LiteralPath $sourceRegistry | ConvertFrom-Json
if ($registry.registry_version -ne 'ukrainian-stage-7-remote-llm-models-v1') {
    throw 'Remote model registry version differs.'
}
if ($OwnerLaptopAddress -ne [string]$registry.target_host_contract.owner_laptop_ipv4) {
    throw 'OwnerLaptopAddress differs from the frozen private-LAN registry.'
}
$serviceAddress = [string]$registry.target_host_contract.service_host_ipv4
$hostAddress = Get-NetIPAddress -AddressFamily IPv4 -IPAddress $serviceAddress -ErrorAction SilentlyContinue
if ($null -eq $hostAddress) {
    throw "The frozen service address is not assigned to this host: $serviceAddress"
}
$drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
if ($null -eq $drive -or [uint64]$drive.FreeSpace -lt 40000000000) {
    throw 'At least 40 GB free on D: is required for the frozen pilot models and runtime.'
}
$nvidia = Get-Command nvidia-smi -ErrorAction Stop | Select-Object -First 1
$gpuLine = & $nvidia.Source '--query-gpu=name,memory.total,compute_cap' '--format=csv,noheader,nounits' 2>$null | Select-Object -First 1
$gpuParts = @($gpuLine -split ',' | ForEach-Object { $_.Trim() })
if ($gpuParts.Count -lt 3 -or [int]$gpuParts[1] -lt 12200) {
    throw 'The verified RTX 4070 SUPER / 12 GB VRAM contract is not satisfied.'
}

$runtimeRoot = Join-Path $ServiceRoot 'runtime'
$downloadsRoot = Join-Path $ServiceRoot 'downloads'
$configRoot = Join-Path $ServiceRoot 'config'
$scriptsRoot = Join-Path $ServiceRoot 'scripts'
$modelsRoot = Join-Path $ServiceRoot 'models'
$logsRoot = Join-Path $ServiceRoot 'logs'
$stateRoot = Join-Path $ServiceRoot 'state'
New-Item -ItemType Directory -Force -Path $runtimeRoot, $downloadsRoot, $configRoot, $scriptsRoot, $modelsRoot, $logsRoot, $stateRoot | Out-Null

Copy-Item -LiteralPath $sourceRegistry -Destination (Join-Path $configRoot 'stage7_remote_llm_models.json') -Force
Copy-Item -LiteralPath $sourceService -Destination (Join-Path $scriptsRoot 'stage7_remote_llm_host_service.ps1') -Force
Copy-Item -LiteralPath $sourceTask -Destination (Join-Path $scriptsRoot 'stage7_remote_llm_task.ps1') -Force

$curl = Get-Command curl.exe -ErrorAction Stop | Select-Object -First 1
foreach ($archive in $registry.runtime.archives) {
    $archivePath = Join-Path $downloadsRoot $archive.filename
    $downloadNeeded = $true
    if (Test-Path -LiteralPath $archivePath -PathType Leaf) {
        $info = Get-Item -LiteralPath $archivePath
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archivePath).Hash.ToLowerInvariant()
        if ([uint64]$info.Length -eq [uint64]$archive.size_bytes -and $hash -eq $archive.sha256) {
            $downloadNeeded = $false
        }
        else {
            throw "Existing runtime archive differs; refusing overwrite: $archivePath"
        }
    }
    if ($downloadNeeded) {
        $partial = $archivePath + '.partial'
        & $curl.Source '-L' '--fail' '--retry' '5' '--continue-at' '-' '--output' $partial $archive.url
        if ($LASTEXITCODE -ne 0) { throw "Runtime download failed: $($archive.url)" }
        $info = Get-Item -LiteralPath $partial
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $partial).Hash.ToLowerInvariant()
        if ([uint64]$info.Length -ne [uint64]$archive.size_bytes -or $hash -ne $archive.sha256) {
            throw "Runtime archive digest differs; partial retained: $partial"
        }
        Move-Item -LiteralPath $partial -Destination $archivePath
    }
    Expand-Archive -LiteralPath $archivePath -DestinationPath $runtimeRoot -Force
}

$runtimePath = Join-Path $runtimeRoot 'llama-server.exe'
if (-not (Test-Path -LiteralPath $runtimePath -PathType Leaf)) {
    throw "llama-server.exe was not extracted to $runtimeRoot"
}
$runtimeVersion = Invoke-NativeCapture -FilePath $runtimePath -ArgumentList @('--version')
$devices = Invoke-NativeCapture -FilePath $runtimePath -ArgumentList @('--list-devices')
if ($devices -notmatch 'CUDA0') {
    throw 'CUDA0 is absent from the pinned llama.cpp runtime device list.'
}

$sshCapability = Get-WindowsCapability -Online -Name 'OpenSSH.Server~~~~0.0.1.0'
if ($sshCapability.State -ne 'Installed') {
    Add-WindowsCapability -Online -Name 'OpenSSH.Server~~~~0.0.1.0' | Out-Null
}
Set-Service -Name sshd -StartupType Automatic
Start-Service -Name sshd

$publicKey = (Get-Content -Raw -Encoding UTF8 -LiteralPath $publicKeyPath).Trim()
if ($publicKey -notmatch '^ssh-ed25519\s+[A-Za-z0-9+/=]+(?:\s+.*)?$') {
    throw 'The supplied owner public key is not one valid ssh-ed25519 line.'
}
$sshRoot = Join-Path $env:ProgramData 'ssh'
New-Item -ItemType Directory -Force -Path $sshRoot | Out-Null
$authorizedKeys = Join-Path $sshRoot 'administrators_authorized_keys'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($authorizedKeys, $publicKey + "`n", $utf8NoBom)
$acl = New-Object Security.AccessControl.FileSecurity
$acl.SetAccessRuleProtection($true, $false)
foreach ($sidValue in @('S-1-5-18', 'S-1-5-32-544')) {
    $sid = New-Object Security.Principal.SecurityIdentifier($sidValue)
    $rule = New-Object Security.AccessControl.FileSystemAccessRule(
        $sid,
        [Security.AccessControl.FileSystemRights]::FullControl,
        [Security.AccessControl.AccessControlType]::Allow
    )
    $acl.AddAccessRule($rule)
}
Set-Acl -LiteralPath $authorizedKeys -AclObject $acl

$sshRule = Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue
if ($null -eq $sshRule) {
    New-NetFirewallRule -Name 'Revelation-Stage7-SSH-22' -DisplayName 'Revelation Stage 7 SSH from owner laptop' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 -RemoteAddress $OwnerLaptopAddress -Profile Private | Out-Null
}
else {
    Set-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -Enabled True -Profile Private -Action Allow
    Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' | Get-NetFirewallAddressFilter | Set-NetFirewallAddressFilter -RemoteAddress $OwnerLaptopAddress
}
$llamaRule = Get-NetFirewallRule -Name 'Revelation-Stage7-LLM-8080' -ErrorAction SilentlyContinue
if ($null -eq $llamaRule) {
    New-NetFirewallRule -Name 'Revelation-Stage7-LLM-8080' -DisplayName 'Revelation Stage 7 llama-server from owner laptop' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8080 -RemoteAddress $OwnerLaptopAddress -Profile Private | Out-Null
}
else {
    Set-NetFirewallRule -Name 'Revelation-Stage7-LLM-8080' -Enabled True -Profile Private -Action Allow
    Get-NetFirewallRule -Name 'Revelation-Stage7-LLM-8080' | Get-NetFirewallAddressFilter | Set-NetFirewallAddressFilter -RemoteAddress $OwnerLaptopAddress
}

$taskScript = Join-Path $scriptsRoot 'stage7_remote_llm_task.ps1'
$taskAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$taskScript`""
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $identity.Name -LogonType S4U -RunLevel Highest
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([timespan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $taskName -Action $taskAction -Principal $taskPrincipal -Settings $taskSettings -Force | Out-Null

$serviceScript = Join-Path $scriptsRoot 'stage7_remote_llm_host_service.ps1'
if (-not $SkipModelDownloads) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $serviceScript -Action InstallModels -ModelId all
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$manifestPath = Join-Path $configRoot 'install_manifest.json'
$manifest = [ordered]@{
    schema_version = 1
    registry_version = $registry.registry_version
    status = if ($SkipModelDownloads) { 'remote_runtime_ready_models_not_downloaded' } else { 'remote_runtime_and_pilot_models_ready' }
    service_root = $ServiceRoot
    owner_laptop_ipv4 = $OwnerLaptopAddress
    service_host_ipv4 = $serviceAddress
    host = $env:COMPUTERNAME
    account = $identity.Name
    gpu = [ordered]@{ name = $gpuParts[0]; memory_total_mib = [int]$gpuParts[1]; compute_capability = $gpuParts[2] }
    runtime = [ordered]@{
        path = $runtimePath
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $runtimePath).Hash.ToLowerInvariant()
        version = $runtimeVersion
        devices = $devices
    }
    openssh = [ordered]@{ service = [string](Get-Service sshd).Status; authorized_key_type = 'ssh-ed25519' }
    scheduled_task = $taskName
    installed_model_ids = if ($SkipModelDownloads) { @() } else { @($registry.models.model_id) }
    completed_at_utc = [datetime]::UtcNow.ToString('o')
    processed_count = 1
    skipped_count = if ($SkipModelDownloads) { $registry.models.Count } else { 0 }
    error_count = 0
}
[IO.File]::WriteAllText($manifestPath, (($manifest | ConvertTo-Json -Depth 12) + "`n"), $utf8NoBom)

Write-Host "Remote Stage 7 LLM host setup complete. Manifest: $manifestPath"
Write-Host 'The server is stopped by default and is reachable only from the registered owner laptop.'
