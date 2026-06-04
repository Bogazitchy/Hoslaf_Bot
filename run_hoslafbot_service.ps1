$ErrorActionPreference = "Continue"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$BotFile = Join-Path $ProjectDir "bot.py"
$LogDir = Join-Path $ProjectDir "logs"
$ServiceLog = Join-Path $LogDir "hoslafbot-runner.log"
$StdOutLog = Join-Path $LogDir "hoslafbot-process.out.log"
$StdErrLog = Join-Path $LogDir "hoslafbot-process.err.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Set-Location $ProjectDir

$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PATH = "$ProjectDir;$env:PATH"

function Write-RunnerLog($Message) {
    Add-Content -Path $ServiceLog -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
}

Write-RunnerLog "HoslafBot runner started."
Start-Sleep -Seconds 60

while ($true) {
    Write-RunnerLog "Starting bot process..."

    $process = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList $BotFile `
        -WorkingDirectory $ProjectDir `
        -RedirectStandardOutput $StdOutLog `
        -RedirectStandardError $StdErrLog `
        -WindowStyle Hidden `
        -PassThru `
        -Wait

    Write-RunnerLog "Bot process exited with code $($process.ExitCode). Restarting in 30 seconds..."
    Start-Sleep -Seconds 30
}
