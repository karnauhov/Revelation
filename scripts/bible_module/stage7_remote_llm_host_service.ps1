param(
    [ValidateSet('InstallModels', 'ListModels', 'Start', 'Stop', 'Status')]
    [string]$Action = 'Status',

    [string]$ModelId = 'all'
)

$ErrorActionPreference = 'Stop'
$serviceRoot = 'D:\RevelationStage7LLM'
$registryPath = Join-Path $serviceRoot 'config\stage7_remote_llm_models.json'
$activePath = Join-Path $serviceRoot 'config\active_model.json'
$runtimePath = Join-Path $serviceRoot 'runtime\llama-server.exe'
$statePath = Join-Path $serviceRoot 'state\server_state.json'
$taskName = 'RevelationStage7LlamaServer'

function Write-StableJsonOutput {
    param([object]$Value)
    Write-Output ($Value | ConvertTo-Json -Depth 12 -Compress)
}

function Write-StableJsonFile {
    param([string]$Path, [object]$Value)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText(
        $Path,
        (($Value | ConvertTo-Json -Depth 12 -Compress) + "`n"),
        $utf8NoBom
    )
}

function Get-Registry {
    if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
        throw "Frozen remote model registry is missing: $registryPath"
    }
    return Get-Content -Raw -Encoding UTF8 -LiteralPath $registryPath | ConvertFrom-Json
}

function Get-RegisteredModel {
    param([object]$Registry, [string]$Id)
    if ($Id -notmatch '^[a-z0-9_]+$') {
        throw 'ModelId contains forbidden characters.'
    }
    $model = $Registry.models | Where-Object model_id -eq $Id | Select-Object -First 1
    if ($null -eq $model) {
        throw "Unknown frozen remote model: $Id"
    }
    return $model
}

function Get-ServiceStatus {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    $health = $null
    $servedModel = $null
    $serviceAddress = [string]$registry.target_host_contract.service_host_ipv4
    try {
        $health = Invoke-RestMethod -Uri "http://$serviceAddress`:8080/health" -TimeoutSec 2
        $models = Invoke-RestMethod -Uri "http://$serviceAddress`:8080/v1/models" -TimeoutSec 3
        if ($models.data.Count -gt 0) { $servedModel = $models.data[0].id }
    }
    catch { }
    $active = $null
    if (Test-Path -LiteralPath $activePath -PathType Leaf) {
        $active = Get-Content -Raw -Encoding UTF8 -LiteralPath $activePath | ConvertFrom-Json
    }
    $gpu = $null
    $nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $nvidia) {
        try {
            $row = & $nvidia.Source '--query-gpu=name,memory.total,memory.used,utilization.gpu' '--format=csv,noheader,nounits' 2>$null | Select-Object -First 1
            $parts = @($row -split ',' | ForEach-Object { $_.Trim() })
            $gpu = [ordered]@{
                name = $parts[0]
                memory_total_mib = [int]$parts[1]
                memory_used_mib = [int]$parts[2]
                utilization_percent = [int]$parts[3]
            }
        }
        catch { }
    }
    return [ordered]@{
        schema_version = 1
        status = if ($null -ne $health -and $health.status -eq 'ok') { 'ready' } elseif ($null -ne $task -and [string]$task.State -eq 'Running') { 'starting' } else { 'stopped' }
        scheduled_task_state = if ($null -eq $task) { 'missing' } else { [string]$task.State }
        active_model_id = if ($null -eq $active) { $null } else { $active.model_id }
        served_model_id = $servedModel
        endpoint = "http://$serviceAddress`:8080"
        gpu = $gpu
        updated_at_utc = [datetime]::UtcNow.ToString('o')
        processed_count = 1
        skipped_count = 0
        error_count = 0
    }
}

$registry = Get-Registry

if ($Action -eq 'ListModels') {
    Write-StableJsonOutput ([ordered]@{
            schema_version = 1
            registry_version = $registry.registry_version
            models = @($registry.models | ForEach-Object {
                    [ordered]@{
                        model_id = $_.model_id
                        role = $_.role
                        repository = $_.repository
                        commit = $_.commit
                        reasoning = $_.reasoning
                        reasoning_budget = $_.reasoning_budget
                        context_tokens = $_.context_tokens
                    }
                })
            processed_count = $registry.models.Count
            skipped_count = 0
            error_count = 0
        })
    exit 0
}

if ($Action -eq 'Status') {
    Write-StableJsonOutput (Get-ServiceStatus)
    exit 0
}

if ($Action -eq 'InstallModels') {
    $status = Get-ServiceStatus
    if ($status.status -ne 'stopped') {
        throw 'Stop the remote model server before downloading or verifying models.'
    }
    $models = if ($ModelId -eq 'all') {
        @($registry.models)
    }
    else {
        @(Get-RegisteredModel -Registry $registry -Id $ModelId)
    }
    $curl = Get-Command curl.exe -ErrorAction Stop | Select-Object -First 1
    $results = @()
    foreach ($model in $models) {
        $modelRoot = Join-Path $serviceRoot (Join-Path 'models' $model.model_id)
        New-Item -ItemType Directory -Force -Path $modelRoot | Out-Null
        foreach ($file in $model.files) {
            $target = Join-Path $modelRoot $file.filename
            $partial = $target + '.partial'
            $state = 'downloaded_and_verified'
            if (Test-Path -LiteralPath $target -PathType Leaf) {
                $info = Get-Item -LiteralPath $target
                $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLowerInvariant()
                if ([uint64]$info.Length -ne [uint64]$file.size_bytes -or $hash -ne $file.sha256) {
                    throw "Existing registered model file differs; refusing overwrite: $target"
                }
                $state = 'already_present_and_verified'
            }
            else {
                & $curl.Source '-L' '--fail' '--retry' '5' '--continue-at' '-' '--output' $partial $file.url
                if ($LASTEXITCODE -ne 0) { throw "Download failed: $($file.url)" }
                $info = Get-Item -LiteralPath $partial
                $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $partial).Hash.ToLowerInvariant()
                if ([uint64]$info.Length -ne [uint64]$file.size_bytes -or $hash -ne $file.sha256) {
                    throw "Downloaded model file digest differs; partial retained: $partial"
                }
                Move-Item -LiteralPath $partial -Destination $target
            }
            $results += [ordered]@{
                model_id = $model.model_id
                filename = $file.filename
                status = $state
                size_bytes = [uint64]$file.size_bytes
                sha256 = $file.sha256
            }
        }
    }
    Write-StableJsonOutput ([ordered]@{
            schema_version = 1
            registry_version = $registry.registry_version
            status = 'complete_registered_model_installation'
            files = $results
            processed_count = $results.Count
            skipped_count = 0
            error_count = 0
        })
    exit 0
}

if ($Action -eq 'Stop') {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($null -ne $task -and [string]$task.State -eq 'Running') {
        Stop-ScheduledTask -TaskName $taskName
    }
    if (Test-Path -LiteralPath $statePath -PathType Leaf) {
        $state = Get-Content -Raw -Encoding UTF8 -LiteralPath $statePath | ConvertFrom-Json
        if ($null -ne $state.process_id) {
            $process = Get-Process -Id ([int]$state.process_id) -ErrorAction SilentlyContinue
            if ($null -ne $process) {
                $expected = (Resolve-Path -LiteralPath $runtimePath).Path
                if ($process.Path -ne $expected) {
                    throw 'Recorded PID belongs to another executable; refusing to stop it.'
                }
                Stop-Process -Id $process.Id
                $process.WaitForExit()
            }
        }
    }
    Start-Sleep -Seconds 1
    Write-StableJsonOutput (Get-ServiceStatus)
    exit 0
}

if ($Action -eq 'Start') {
    $model = Get-RegisteredModel -Registry $registry -Id $ModelId
    $status = Get-ServiceStatus
    if ($status.status -ne 'stopped') {
        if ($status.status -eq 'ready' -and $status.active_model_id -eq $model.model_id) {
            Write-StableJsonOutput $status
            exit 0
        }
        throw 'Another remote model is starting or running; stop it before switching.'
    }
    foreach ($file in $model.files) {
        $path = Join-Path $serviceRoot (Join-Path (Join-Path 'models' $model.model_id) $file.filename)
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Model is not installed: $path"
        }
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $activePath) | Out-Null
    Write-StableJsonFile -Path $activePath -Value ([ordered]@{
            schema_version = 1
            registry_version = $registry.registry_version
            model_id = $model.model_id
            selected_at_utc = [datetime]::UtcNow.ToString('o')
        })
    Start-ScheduledTask -TaskName $taskName
    $deadline = [datetime]::UtcNow.AddMinutes(5)
    do {
        Start-Sleep -Seconds 2
        $status = Get-ServiceStatus
        if ($status.status -eq 'ready') {
            Write-StableJsonOutput $status
            exit 0
        }
        if ($status.scheduled_task_state -ne 'Running') {
            throw 'Remote llama-server task stopped before becoming ready; inspect D:\RevelationStage7LLM\logs.'
        }
    } while ([datetime]::UtcNow -lt $deadline)
    throw 'Remote llama-server did not become ready within five minutes.'
}
