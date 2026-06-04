$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServiceExe = Join-Path $ProjectDir "HoslafBotService.exe"

Set-Location $ProjectDir

$service = Get-Service -Name HoslafBot -ErrorAction SilentlyContinue
if ($service) {
    & $ServiceExe refresh
} else {
    & $ServiceExe install
}

sc.exe config HoslafBot start= delayed-auto | Out-Null
sc.exe failure HoslafBot reset= 86400 actions= restart/10000/restart/30000/restart/60000 | Out-Null
sc.exe failureflag HoslafBot 1 | Out-Null

$service = Get-Service -Name HoslafBot
if ($service.Status -ne "Running") {
    & $ServiceExe start
}
