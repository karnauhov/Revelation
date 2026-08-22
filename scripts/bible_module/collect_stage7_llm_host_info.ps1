param(
    [string]$OutputDirectory = ''
)

$ErrorActionPreference = 'Stop'
$schemaVersion = 1
$probeVersion = 'ukrainian-stage-7-local-llm-host-probe-v1'

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
    $OutputDirectory = Join-Path $desktop 'Revelation-stage7-host-info'
}

function Invoke-SafeTextCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [string[]]$Arguments = @()
    )

    $resolved = Get-Command $Command -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $resolved) {
        return $null
    }
    try {
        $text = & $resolved.Source @Arguments 2>$null | Out-String
        return [ordered]@{
            path = $resolved.Source
            version_output = $text.Trim()
            exit_code = $LASTEXITCODE
        }
    }
    catch {
        return [ordered]@{
            path = $resolved.Source
            version_output = ''
            exit_code = -1
            error = $_.Exception.Message
        }
    }
}

function Convert-ToIsoUtc {
    param([object]$Value)
    if ($null -eq $Value) { return $null }
    try {
        return ([Management.ManagementDateTimeConverter]::ToDateTime([string]$Value)).ToUniversalTime().ToString('o')
    }
    catch {
        try { return ([datetime]$Value).ToUniversalTime().ToString('o') }
        catch { return [string]$Value }
    }
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$outputRoot = (Resolve-Path -LiteralPath $OutputDirectory).Path
$jsonPath = Join-Path $outputRoot 'stage7_llm_host_info.json'
$reportPath = Join-Path $outputRoot 'README.ru.md'

$os = Get-CimInstance Win32_OperatingSystem
$computer = Get-CimInstance Win32_ComputerSystem
$processors = @(Get-CimInstance Win32_Processor | Sort-Object DeviceID | ForEach-Object {
        [ordered]@{
            name = $_.Name.Trim()
            physical_cores = [int]$_.NumberOfCores
            logical_processors = [int]$_.NumberOfLogicalProcessors
            max_clock_mhz = [int]$_.MaxClockSpeed
            virtualization_firmware_enabled = [bool]$_.VirtualizationFirmwareEnabled
        }
    })
$memoryModules = @(Get-CimInstance Win32_PhysicalMemory | Sort-Object DeviceLocator | ForEach-Object {
        [ordered]@{
            capacity_bytes = [uint64]$_.Capacity
            configured_clock_mhz = [int]$_.ConfiguredClockSpeed
            speed_mhz = [int]$_.Speed
        }
    })
$displayAdapters = @(Get-CimInstance Win32_VideoController | Sort-Object Name | ForEach-Object {
        [ordered]@{
            name = $_.Name
            adapter_ram_reported_bytes = if ($null -eq $_.AdapterRAM) { $null } else { [uint64]$_.AdapterRAM }
            driver_version = $_.DriverVersion
            driver_date_utc = Convert-ToIsoUtc $_.DriverDate
            video_processor = $_.VideoProcessor
            status = $_.Status
        }
    })
$fixedDisks = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Sort-Object DeviceID | ForEach-Object {
        [ordered]@{
            drive = $_.DeviceID
            filesystem = $_.FileSystem
            size_bytes = [uint64]$_.Size
            free_bytes = [uint64]$_.FreeSpace
        }
    })

$privateIpv4 = @()
try {
    $privateIpv4 = @(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
            Where-Object {
                $_.IPAddress -ne '127.0.0.1' -and
                -not $_.IPAddress.StartsWith('169.254.')
            } |
            Sort-Object InterfaceAlias, IPAddress |
            ForEach-Object {
                [ordered]@{
                    interface = $_.InterfaceAlias
                    address = $_.IPAddress
                    prefix_length = [int]$_.PrefixLength
                    address_state = [string]$_.AddressState
                }
            })
}
catch { $privateIpv4 = @() }

$networkProfiles = @()
try {
    $networkProfiles = @(Get-NetConnectionProfile -ErrorAction Stop |
            Sort-Object InterfaceAlias |
            ForEach-Object {
                [ordered]@{
                    interface = $_.InterfaceAlias
                    network_category = [string]$_.NetworkCategory
                    ipv4_connectivity = [string]$_.IPv4Connectivity
                }
            })
}
catch { $networkProfiles = @() }

$nvidia = [ordered]@{ available = $false; gpus = @(); command = $null }
$nvidiaCommand = Get-Command nvidia-smi -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -ne $nvidiaCommand) {
    $nvidia.available = $true
    $nvidia.command = $nvidiaCommand.Source
    try {
        $gpuRows = @(& $nvidiaCommand.Source '--query-gpu=index,name,driver_version,memory.total,compute_cap' '--format=csv,noheader,nounits' 2>$null)
        $nvidia.gpus = @($gpuRows | ForEach-Object {
                $parts = @($_ -split ',' | ForEach-Object { $_.Trim() })
                [ordered]@{
                    index = [int]$parts[0]
                    name = $parts[1]
                    driver_version = $parts[2]
                    memory_total_mib = [int]$parts[3]
                    compute_capability = $parts[4]
                }
            })
    }
    catch {
        $nvidia.error = $_.Exception.Message
        $nvidia.gpus = @()
    }
}

$sshd = Get-Service sshd -ErrorAction SilentlyContinue
$openSshCapability = $null
try {
    $capability = Get-WindowsCapability -Online -Name 'OpenSSH.Server~~~~0.0.1.0' -ErrorAction Stop
    $openSshCapability = [string]$capability.State
}
catch { $openSshCapability = 'unknown_or_requires_elevation' }

$listeners = [ordered]@{ ssh_22 = $false; llama_8080 = $false }
try {
    $listeners.ssh_22 = $null -ne (Get-NetTCPConnection -State Listen -LocalPort 22 -ErrorAction SilentlyContinue | Select-Object -First 1)
    $listeners.llama_8080 = $null -ne (Get-NetTCPConnection -State Listen -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -First 1)
}
catch { }

$vulkan = Invoke-SafeTextCommand -Command 'vulkaninfo' -Arguments @('--summary')
if ($null -ne $vulkan -and -not [string]::IsNullOrWhiteSpace($vulkan.version_output)) {
    $safeVulkanLines = @($vulkan.version_output -split "`r?`n" | Where-Object {
            $_ -match '^Vulkan Instance Version:' -or
            $_ -match '^\s*(apiVersion|driverVersion|deviceType|deviceName|driverName|driverInfo)\s*='
        })
    $vulkan.version_output = ($safeVulkanLines -join "`n").Trim()
}

$tools = [ordered]@{
    winget = Invoke-SafeTextCommand -Command 'winget' -Arguments @('--version')
    python = Invoke-SafeTextCommand -Command 'python' -Arguments @('--version')
    git = Invoke-SafeTextCommand -Command 'git' -Arguments @('--version')
    ssh = Invoke-SafeTextCommand -Command 'ssh' -Arguments @('-V')
    curl = Invoke-SafeTextCommand -Command 'curl.exe' -Arguments @('--version')
    llama_server = Invoke-SafeTextCommand -Command 'llama-server' -Arguments @('--version')
    nvcc = Invoke-SafeTextCommand -Command 'nvcc' -Arguments @('--version')
    vulkaninfo = $vulkan
}

$probeSha = $null
if (-not [string]::IsNullOrWhiteSpace($PSCommandPath) -and (Test-Path -LiteralPath $PSCommandPath -PathType Leaf)) {
    $probeSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $PSCommandPath).Hash.ToLowerInvariant()
}

$payload = [ordered]@{
    schema_version = $schemaVersion
    probe_version = $probeVersion
    status = 'complete_read_only_host_inventory'
    collected_at_utc = [datetime]::UtcNow.ToString('o')
    probe_script_sha256 = $probeSha
    host = [ordered]@{
        computer_name = $env:COMPUTERNAME
        manufacturer = $computer.Manufacturer
        model = $computer.Model
        system_type = $computer.SystemType
    }
    operating_system = [ordered]@{
        caption = $os.Caption
        version = $os.Version
        build_number = $os.BuildNumber
        architecture = $os.OSArchitecture
        last_boot_utc = Convert-ToIsoUtc $os.LastBootUpTime
        powershell_version = $PSVersionTable.PSVersion.ToString()
    }
    processors = $processors
    memory = [ordered]@{
        total_physical_bytes = [uint64]$computer.TotalPhysicalMemory
        modules = $memoryModules
    }
    display_adapters = $displayAdapters
    nvidia_smi = $nvidia
    fixed_disks = $fixedDisks
    network = [ordered]@{
        private_ipv4 = $privateIpv4
        profiles = $networkProfiles
        listeners = $listeners
        openssh_server_capability = $openSshCapability
        sshd_service_status = if ($null -eq $sshd) { 'not_installed' } else { [string]$sshd.Status }
        note = 'No MAC addresses, public IP, DNS configuration, credentials, or serial numbers collected.'
    }
    tools = $tools
    privacy = [ordered]@{
        collected = @('hardware capacity', 'driver versions', 'private LAN address', 'tool availability')
        excluded = @('serial numbers', 'MAC addresses', 'public IP', 'credentials', 'environment variables', 'user files')
    }
    processed_count = 1
    skipped_count = 0
    error_count = 0
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$json = $payload | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText($jsonPath, $json + "`n", $utf8NoBom)
$jsonSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $jsonPath).Hash.ToLowerInvariant()

$gpuSummary = if ($nvidia.available -and $nvidia.gpus.Count -gt 0) {
    ($nvidia.gpus | ForEach-Object { "- NVIDIA GPU $($_.index): $($_.name), $($_.memory_total_mib) MiB VRAM, compute $($_.compute_capability), driver $($_.driver_version)" }) -join "`n"
}
else {
    ($displayAdapters | ForEach-Object { "- Display adapter: $($_.name), driver $($_.driver_version)" }) -join "`n"
}
$ipSummary = if ($privateIpv4.Count -gt 0) {
    ($privateIpv4 | ForEach-Object { "- $($_.interface): $($_.address)/$($_.prefix_length)" }) -join "`n"
}
else { '- Private IPv4 address not detected.' }
$cpuSummary = ($processors | ForEach-Object { "- $($_.name): $($_.physical_cores) cores / $($_.logical_processors) threads" }) -join "`n"
$ramGiB = [math]::Round([double]$computer.TotalPhysicalMemory / 1GB, 2)

$report = @"
# Инвентаризация компьютера для локальной LLM этапа 7

- Probe: ``$probeVersion``
- Собрано UTC: ``$($payload.collected_at_utc)``
- Компьютер: ``$($payload.host.computer_name)`` — $($computer.Manufacturer) $($computer.Model)
- ОС: $($os.Caption), $($os.OSArchitecture), build $($os.BuildNumber)
- RAM: **$ramGiB GiB**
- OpenSSH Server: ``$openSshCapability``; служба ``$($payload.network.sshd_service_status)``
- SHA-256 JSON: ``$jsonSha``

## CPU

$cpuSummary

## GPU

$gpuSummary

## Адреса локальной сети

$ipSummary

## Что передать для анализа

Передайте оба файла из этой папки: ``stage7_llm_host_info.json`` и ``README.ru.md``.
Они не содержат паролей, ключей, MAC-адресов, публичного IP, серийных номеров или
содержимого пользовательских файлов.
"@
[IO.File]::WriteAllText($reportPath, $report.TrimEnd() + "`n", $utf8NoBom)

Write-Host "Готово. Передайте для анализа два файла из: $outputRoot"
Write-Host "JSON: $jsonPath"
Write-Host "Отчёт: $reportPath"
