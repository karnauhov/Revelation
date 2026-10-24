param(
    [ValidateSet('completed', 'stopped')]
    [string]$Status = 'completed'
)

$soundName = if ($Status -eq 'completed') {
    'Ring06.wav'
} else {
    'Windows Critical Stop.wav'
}
$repeatCount = if ($Status -eq 'completed') { 1 } else { 3 }
$soundPath = Join-Path $env:WINDIR "Media\$soundName"
$player = New-Object System.Media.SoundPlayer $soundPath
try {
    $player.Load()
    for ($repeat = 0; $repeat -lt $repeatCount; $repeat++) {
        $player.PlaySync()
        if ($repeat -lt ($repeatCount - 1)) { Start-Sleep -Milliseconds 350 }
    }
} finally {
    $player.Dispose()
}
