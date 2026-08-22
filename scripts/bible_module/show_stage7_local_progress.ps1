$ErrorActionPreference = 'Stop'
$project = 'C:\Users\karna\Projects\Revelation'
$batchRoot = Join-Path $project 'scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm'

Set-Location -LiteralPath $project
python -B -m scripts.bible_module.ukrainian_stage_7_local_llm_batch status --batch-root $batchRoot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Get-Content -LiteralPath (Join-Path $batchRoot 'STATUS.ru.md') -Encoding utf8
