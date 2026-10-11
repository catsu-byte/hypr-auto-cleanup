$ErrorActionPreference = 'Stop'

$InstallDirectory = Join-Path $env:LOCALAPPDATA 'HyprAutoCleanup'
$Target = Join-Path $InstallDirectory 'auto_cleanup.ps1'
$StartupDirectory = [Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupDirectory 'Hypr Auto-Cleanup.lnk'
$Source = Join-Path $PSScriptRoot 'auto_cleanup.ps1'

New-Item -ItemType Directory -Force -Path $InstallDirectory | Out-Null
Copy-Item -Force $Source $Target

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = 'powershell.exe'
$Shortcut.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Target`""
$Shortcut.WorkingDirectory = $InstallDirectory
$Shortcut.Save()

Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @(
    '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$Target`""
)

Write-Host "Installed to $InstallDirectory"
Write-Host 'Hypr Auto-Cleanup is running and will start when you sign in.'
