$ErrorActionPreference = 'Stop'

$InstallDirectory = Join-Path $env:LOCALAPPDATA 'HyprAutoCleanup'
$Target = Join-Path $InstallDirectory 'auto_cleanup.ps1'
$ShortcutPath = Join-Path ([Environment]::GetFolderPath('Startup')) 'Hypr Auto-Cleanup.lnk'

Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe' OR Name = 'pwsh.exe'" |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Target) } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

if (Test-Path $ShortcutPath) { Remove-Item -Force $ShortcutPath }
if (Test-Path $InstallDirectory) { Remove-Item -Recurse -Force $InstallDirectory }

Write-Host 'Hypr Auto-Cleanup was removed.'
