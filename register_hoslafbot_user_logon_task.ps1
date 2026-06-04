$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunnerScript = Join-Path $ProjectDir "run_hoslafbot_service.ps1"
$TaskName = "HoslafBotUserLogon"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$RunnerScript`""

$trigger = New-ScheduledTaskTrigger -AtLogOn
$trigger.Delay = "PT20S"

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Starts Hoslaf Discord Bot when the current Windows user logs in." `
    -Force

Start-ScheduledTask -TaskName $TaskName
Get-ScheduledTask -TaskName $TaskName
