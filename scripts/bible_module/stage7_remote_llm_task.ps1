$ErrorActionPreference = 'Stop'
$serviceRoot = 'D:\RevelationStage7LLM'
$registryPath = Join-Path $serviceRoot 'config\stage7_remote_llm_models.json'
$activePath = Join-Path $serviceRoot 'config\active_model.json'
$runtimePath = Join-Path $serviceRoot 'runtime\llama-server.exe'
$statePath = Join-Path $serviceRoot 'state\server_state.json'
$logsRoot = Join-Path $serviceRoot 'logs'

function Write-StableJson {
    param([string]$Path, [object]$Value)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText(
        $Path,
        (($Value | ConvertTo-Json -Depth 12 -Compress) + "`n"),
        $utf8NoBom
    )
}

foreach ($required in @($registryPath, $activePath, $runtimePath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required remote LLM file is missing: $required"
    }
}

$registry = Get-Content -Raw -Encoding UTF8 -LiteralPath $registryPath | ConvertFrom-Json
$active = Get-Content -Raw -Encoding UTF8 -LiteralPath $activePath | ConvertFrom-Json
$serviceAddress = [string]$registry.target_host_contract.service_host_ipv4
if ($serviceAddress -notmatch '^192\.168\.1\.\d{1,3}$') {
    throw 'Frozen service host address is outside the expected private LAN.'
}
$model = $registry.models | Where-Object model_id -eq $active.model_id | Select-Object -First 1
if ($null -eq $model) {
    throw "Active model is absent from the frozen registry: $($active.model_id)"
}

$modelRoot = Join-Path $serviceRoot (Join-Path 'models' $model.model_id)
$modelFile = $model.files | Where-Object kind -eq 'model' | Select-Object -First 1
$mmprojFile = $model.files | Where-Object kind -eq 'mmproj' | Select-Object -First 1
$modelPath = Join-Path $modelRoot $modelFile.filename
$mmprojPath = Join-Path $modelRoot $mmprojFile.filename
foreach ($item in @(
        @{ Path = $modelPath; Sha = $modelFile.sha256 },
        @{ Path = $mmprojPath; Sha = $mmprojFile.sha256 }
    )) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw "Registered model component is missing: $($item.Path)"
    }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.Path).Hash.ToLowerInvariant()
    if ($actual -ne $item.Sha) {
        throw "Registered model component SHA-256 differs: $($item.Path)"
    }
}

New-Item -ItemType Directory -Force -Path $logsRoot, (Split-Path -Parent $statePath) | Out-Null
$stamp = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$stdoutPath = Join-Path $logsRoot "llama-$($model.model_id)-$stamp.stdout.log"
$stderrPath = Join-Path $logsRoot "llama-$($model.model_id)-$stamp.stderr.log"
$arguments = @(
    '-m', $modelPath,
    '--mmproj', $mmprojPath,
    '--host', $serviceAddress,
    '--port', '8080',
    '-t', '4',
    '-c', [string]$model.context_tokens,
    '-np', '1',
    '-dev', 'CUDA0',
    '-ngl', '99',
    '-mmdev', 'CUDA0',
    '-fa', 'on',
    '--reasoning-format', 'deepseek',
    '-rea', [string]$model.reasoning,
    '--reasoning-budget', [string]$model.reasoning_budget,
    '--no-webui'
)

$process = $null
try {
    $process = Start-Process `
        -FilePath $runtimePath `
        -ArgumentList $arguments `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath
    Write-StableJson -Path $statePath -Value ([ordered]@{
            schema_version = 1
            registry_version = $registry.registry_version
            status = 'starting_or_running'
            model_id = $model.model_id
            process_id = $process.Id
            stdout_path = $stdoutPath
            stderr_path = $stderrPath
            updated_at_utc = [datetime]::UtcNow.ToString('o')
            processed_count = 1
            skipped_count = 0
            error_count = 0
        })
    $process.WaitForExit()
    exit $process.ExitCode
}
finally {
    Write-StableJson -Path $statePath -Value ([ordered]@{
            schema_version = 1
            registry_version = $registry.registry_version
            status = 'stopped'
            model_id = $model.model_id
            process_id = if ($null -eq $process) { $null } else { $process.Id }
            stdout_path = $stdoutPath
            stderr_path = $stderrPath
            updated_at_utc = [datetime]::UtcNow.ToString('o')
            processed_count = 1
            skipped_count = 0
            error_count = if ($null -eq $process -or $process.ExitCode -ne 0) { 1 } else { 0 }
        })
}
