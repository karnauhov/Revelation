# Run against a local Windows Release build of webview_release_probe.dart.
# The host must observe process exit because the crash happens after Dart stops.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Executable,
    [ValidateRange(1, 10)][int]$Repeat = 3
)

$ErrorActionPreference = 'Stop'
$executablePath = (Resolve-Path -LiteralPath $Executable).Path
if (Get-Process ([IO.Path]::GetFileNameWithoutExtension($executablePath)) -ErrorAction SilentlyContinue) {
    throw 'Close the existing Revelation window before starting the shutdown regression.'
}

$scenarios = @(
    @{ Name = 'cold'; Arguments = '--without-webview'; Title = 'Revelation WebView probe - no WebView' },
    @{ Name = 'loading'; Title = 'Revelation WebView probe - starting' },
    @{ Name = 'loaded'; Title = 'Revelation WebView probe - JavaScript verified' }
)
$failures = [System.Collections.Generic.List[string]]::new()
foreach ($scenario in $scenarios) {
    for ($attempt = 1; $attempt -le $Repeat; $attempt++) {
        $start = @{
            FilePath = $executablePath
            WorkingDirectory = Split-Path -Parent $executablePath
            PassThru = $true
        }
        if ($scenario.Arguments) { $start.ArgumentList = $scenario.Arguments }
        $process = Start-Process @start
        try {
            $ready = [Diagnostics.Stopwatch]::StartNew()
            do {
                $process.Refresh()
                if ($process.HasExited) { throw 'Process exited before the close request.' }
                if ($process.MainWindowHandle -ne 0 -and $process.MainWindowTitle -eq $scenario.Title) { break }
                if ($ready.Elapsed.TotalSeconds -ge 25) { throw "Timed out waiting for '$($scenario.Title)'." }
                Start-Sleep -Milliseconds 25
            } while ($true)

            $shutdown = [Diagnostics.Stopwatch]::StartNew()
            if (!$process.CloseMainWindow()) { throw 'Could not deliver the close request.' }
            if (!$process.WaitForExit(15000)) { throw 'Process did not exit after the close request.' }
            $exitHex = '0x{0:X8}' -f $process.ExitCode
            if ($process.ExitCode -ne 0) { throw "Process exited with $exitHex." }

            Write-Output ("{0} {1}/{2}: {3}, PID {4}, {5} ms" -f $scenario.Name, $attempt, $Repeat, $exitHex, $process.Id, $shutdown.ElapsedMilliseconds)
        } catch {
            $failures.Add(("{0} {1}/{2}: {3}" -f $scenario.Name, $attempt, $Repeat, $_.Exception.Message))
        } finally {
            if (!$process.HasExited) {
                $process.Kill()
                $process.WaitForExit()
            }
            $process.Dispose()
        }
    }
}
if ($failures.Count) { throw ($failures -join [Environment]::NewLine) }
