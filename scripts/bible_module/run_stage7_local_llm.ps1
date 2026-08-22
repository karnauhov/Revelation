param(
    [ValidateRange(12, 39)]
    [int]$FromOrdinal = 12,

    [ValidateRange(12, 39)]
    [int]$ToOrdinal = 39,

    [switch]$StatusOnly
)

$ErrorActionPreference = 'Stop'
$project = 'C:\Users\karna\Projects\Revelation'
$batchRoot = Join-Path $project 'scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm'
$server = 'C:\Users\karna\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe'
$snapshot = 'C:\Users\karna\.cache\huggingface\hub\models--unsloth--Qwen3.5-9B-GGUF\snapshots\3885219b6810b007914f3a7950a8d1b469d598a5'
$model = Join-Path $snapshot 'Qwen3.5-9B-Q4_K_M.gguf'
$mmproj = Join-Path $snapshot 'mmproj-BF16.gguf'
$modelSha256 = '03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8'
$mmprojSha256 = '853698ce7aa6c7ba732478bad280240969ddf7b0fcbf93900046f63903a83383'
$endpoint = 'http://127.0.0.1:8080'
$executionStateType = @'
using System;
using System.Runtime.InteropServices;
public static class Stage7ExecutionState {
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern uint SetThreadExecutionState(uint esFlags);
}
'@

Set-Location -LiteralPath $project

if ($StatusOnly) {
    python -B -m scripts.bible_module.ukrainian_stage_7_local_llm_batch status --batch-root $batchRoot
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Get-Content -LiteralPath (Join-Path $batchRoot 'STATUS.ru.md') -Encoding utf8
    exit 0
}

if ($FromOrdinal -gt $ToOrdinal) {
    throw 'FromOrdinal must be less than or equal to ToOrdinal.'
}

foreach ($required in @($server, $model, $mmproj)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required local-LLM file is missing: $required"
    }
}
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $model).Hash.ToLowerInvariant() -ne $modelSha256) {
    throw 'Qwen model SHA-256 differs; refusing an unregistered model.'
}
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $mmproj).Hash.ToLowerInvariant() -ne $mmprojSha256) {
    throw 'Qwen multimodal projector SHA-256 differs; refusing an unregistered component.'
}

python -B -m scripts.bible_module.ukrainian_stage_7_local_llm_batch prepare `
    --batch-root $batchRoot `
    --from-ordinal $FromOrdinal `
    --to-ordinal $ToOrdinal
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$serverWasStarted = $false
$serverProcess = $null
Add-Type -TypeDefinition $executionStateType
[Stage7ExecutionState]::SetThreadExecutionState(0x80000001) | Out-Null
try {
    $serverReady = $false
    try {
        $health = Invoke-RestMethod -Uri "$endpoint/health" -TimeoutSec 3
        $serverReady = $health.status -eq 'ok'
    }
    catch {
        $serverReady = $false
    }

    if (-not $serverReady) {
        $logs = Join-Path $batchRoot 'logs'
        New-Item -ItemType Directory -Path $logs -Force | Out-Null
        $stdout = Join-Path $logs 'llama-server.stdout.log'
        $stderr = Join-Path $logs 'llama-server.stderr.log'
        $arguments = @(
            '-m', $model,
            '--mmproj', $mmproj,
            '--host', '127.0.0.1',
            '--port', '8080',
            '-t', '10',
            '-c', '32768',
            '-np', '1',
            '-dev', 'none',
            '-ngl', '0',
            '--no-op-offload',
            '-mmdev', 'none',
            '-rea', 'off',
            '--reasoning-budget', '0'
        )
        $serverProcess = Start-Process `
            -FilePath $server `
            -ArgumentList $arguments `
            -PassThru `
            -WindowStyle Hidden `
            -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr
        $serverWasStarted = $true

        $deadline = [DateTime]::UtcNow.AddMinutes(3)
        while ([DateTime]::UtcNow -lt $deadline) {
            if ($serverProcess.HasExited) {
                throw "llama-server stopped during startup. Inspect $stderr"
            }
            try {
                $health = Invoke-RestMethod -Uri "$endpoint/health" -TimeoutSec 3
                if ($health.status -eq 'ok') {
                    $serverReady = $true
                    break
                }
            }
            catch {
                Start-Sleep -Seconds 2
            }
        }
        if (-not $serverReady) {
            throw "llama-server did not become ready. Inspect $stderr"
        }
    }

    $models = Invoke-RestMethod -Uri "$endpoint/v1/models" -TimeoutSec 10
    if ($models.data.Count -lt 1 -or $models.data[0].id -notmatch 'Qwen3\.5-9B') {
        throw 'Port 8080 is occupied by an unapproved model; stop that server and rerun.'
    }

    python -B -m scripts.bible_module.ukrainian_stage_7_local_llm_batch run `
        --batch-root $batchRoot `
        --endpoint $endpoint
    $batchExitCode = $LASTEXITCODE
}
finally {
    if ($serverWasStarted -and $null -ne $serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id
        $serverProcess.WaitForExit()
    }
    [Stage7ExecutionState]::SetThreadExecutionState(0x80000000) | Out-Null
}

python -B -m scripts.bible_module.ukrainian_stage_7_local_llm_batch status --batch-root $batchRoot
Get-Content -LiteralPath (Join-Path $batchRoot 'STATUS.ru.md') -Encoding utf8
exit $batchExitCode
