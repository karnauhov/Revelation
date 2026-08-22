param(
    [ValidateSet('TestSsh', 'ListModels', 'InstallModels', 'Start', 'Stop', 'Status', 'BenchmarkAll', 'RunWeekQueue')]
    [string]$Action = 'Status',

    [string]$ModelId = 'qwen35_9b_q8_reasoning1024',
    [string]$RemoteHost = '192.168.1.188',
    [string]$RemoteUser = 'Nazar',
    [string]$IdentityFile = "$env:USERPROFILE\.ssh\id_ed25519"
)

$ErrorActionPreference = 'Stop'
$project = 'C:\Users\karna\Projects\Revelation'
$endpoint = "http://$RemoteHost`:8080"
$remoteService = 'D:\RevelationStage7LLM\scripts\stage7_remote_llm_host_service.ps1'
$batchRoot = Join-Path $project 'scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm'
$template = Join-Path $project 'scripts\bible_module\work\ukrainian_stage_7_20260801\gold_compact_review\pass_2\Ruth\review_pass_2.shard_008.compact.template.jsonl'
$reference = Join-Path $project 'scripts\bible_module\work\ukrainian_stage_7_20260801\gold_compact_review\pass_2\Ruth\completed_qc\review_pass_2.shard_008.raw.qc-v2.jsonl'
$allowedModels = @(
    'qwen35_9b_q8_reasoning1024',
    'ministral3_14b_reasoning_q4km',
    'qwen35_27b_iq2xxs_reasoning1024'
)

if (-not (Test-Path -LiteralPath $IdentityFile -PathType Leaf)) {
    throw "Owner SSH private key is missing: $IdentityFile"
}
if ($RemoteHost -notmatch '^192\.168\.1\.\d{1,3}$' -or $RemoteUser -notmatch '^[A-Za-z0-9_.-]+$') {
    throw 'Remote host or user is outside the expected private-LAN contract.'
}
if ($ModelId -notin $allowedModels -and $ModelId -ne 'all') {
    throw "Unknown frozen remote model: $ModelId"
}

Set-Location -LiteralPath $project

function Invoke-RemoteService {
    param([string]$RemoteAction, [string]$RemoteModelId = 'all')
    $command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File $remoteService -Action $RemoteAction -ModelId $RemoteModelId"
    $output = & ssh.exe '-i' $IdentityFile '-o' 'BatchMode=yes' '-o' 'StrictHostKeyChecking=accept-new' "$RemoteUser@$RemoteHost" $command
    if ($LASTEXITCODE -ne 0) {
        throw "Remote service action failed: $RemoteAction / $RemoteModelId"
    }
    return ($output | Out-String).Trim()
}

function Wait-RemoteHealth {
    $deadline = [datetime]::UtcNow.AddMinutes(15)
    do {
        try {
            $health = Invoke-RestMethod -Uri "$endpoint/health" -TimeoutSec 3
            if ($health.status -eq 'ok') { return }
        }
        catch { }
        Start-Sleep -Seconds 2
    } while ([datetime]::UtcNow -lt $deadline)
    throw "Remote llama-server did not become reachable at $endpoint"
}

function Start-RemoteModel {
    param([string]$Id)
    Write-Host "Starting remote model: $Id"
    Write-Output (Invoke-RemoteService -RemoteAction 'Start' -RemoteModelId $Id)
    Wait-RemoteHealth
}

function Stop-RemoteModel {
    try { Write-Output (Invoke-RemoteService -RemoteAction 'Stop') }
    catch { Write-Warning $_.Exception.Message }
}

if ($Action -eq 'TestSsh') {
    & ssh.exe '-i' $IdentityFile '-o' 'BatchMode=yes' '-o' 'StrictHostKeyChecking=accept-new' "$RemoteUser@$RemoteHost" 'hostname'
    exit $LASTEXITCODE
}
if ($Action -eq 'ListModels') {
    Write-Output (Invoke-RemoteService -RemoteAction 'ListModels')
    exit 0
}
if ($Action -eq 'InstallModels') {
    Write-Output (Invoke-RemoteService -RemoteAction 'InstallModels' -RemoteModelId $ModelId)
    exit 0
}
if ($Action -eq 'Start') {
    Start-RemoteModel -Id $ModelId
    exit 0
}
if ($Action -eq 'Stop') {
    Stop-RemoteModel
    exit 0
}
if ($Action -eq 'Status') {
    Write-Output (Invoke-RemoteService -RemoteAction 'Status')
    exit 0
}

$executionStateType = @'
using System;
using System.Runtime.InteropServices;
public static class Stage7RemoteExecutionState {
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern uint SetThreadExecutionState(uint esFlags);
}
'@
Add-Type -TypeDefinition $executionStateType
[Stage7RemoteExecutionState]::SetThreadExecutionState([uint32]2147483649) | Out-Null
try {
    if ($Action -eq 'BenchmarkAll') {
        $stamp = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
        $outputRoot = Join-Path $batchRoot (Join-Path 'remote_benchmarks' $stamp)
        New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null
        foreach ($candidate in $allowedModels) {
            try {
                Start-RemoteModel -Id $candidate
                $outputDir = Join-Path $outputRoot $candidate
                python -B -m scripts.bible_module.ukrainian_stage_7_local_llm_benchmark `
                    --template $template `
                    --reference $reference `
                    --output-dir $outputDir `
                    --endpoint $endpoint `
                    --variant-id "remote-rtx4070super-$candidate" `
                    --refs 'Ruth.4.18,Ruth.3.5,Ruth.4.8' `
                    --max-tokens 6144 `
                    --max-attempts 3
                if ($LASTEXITCODE -ne 0) {
                    Write-Warning "Benchmark failed for $candidate; responses remain in $outputDir"
                }
            }
            catch {
                Write-Warning "Remote candidate failed: $candidate - $($_.Exception.Message)"
            }
            finally {
                Stop-RemoteModel
            }
        }
        Write-Host "Remote benchmark matrix finished. Results: $outputRoot"
        exit 0
    }

    if ($Action -eq 'RunWeekQueue') {
        $verdictPath = Join-Path $batchRoot 'remote_pilot_verdict.json'
        if (-not (Test-Path -LiteralPath $verdictPath -PathType Leaf)) {
            throw "Weekly queue remains blocked until a reviewed remote pilot verdict exists: $verdictPath"
        }
        $verdict = Get-Content -Raw -Encoding UTF8 -LiteralPath $verdictPath | ConvertFrom-Json
        if ($verdict.passed -ne $true -or $verdict.model_id -ne $ModelId) {
            throw 'Remote pilot verdict does not authorize the requested model.'
        }
        Start-RemoteModel -Id $ModelId
        python -B -m scripts.bible_module.ukrainian_stage_7_local_llm_batch run --batch-root $batchRoot --endpoint $endpoint
        exit $LASTEXITCODE
    }
}
finally {
    if ($Action -eq 'RunWeekQueue') { Stop-RemoteModel }
    [Stage7RemoteExecutionState]::SetThreadExecutionState([uint32]2147483648) | Out-Null
}
