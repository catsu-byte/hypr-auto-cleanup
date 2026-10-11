$ErrorActionPreference = 'Stop'

$CheckIntervalSeconds = 60
$BrowserTimeoutSeconds = 30 * 60
$DefaultTimeoutSeconds = 60 * 60
$Browsers = @('firefox', 'zen', 'chromium', 'brave', 'brave-browser', 'chrome', 'google-chrome')
$NeverClose = @('discord', 'vesktop', 'spotify', 'steam', 'obsidian')
$SystemProcesses = @(
    'applicationframehost', 'dwm', 'explorer', 'lockapp', 'searchhost',
    'shellexperiencehost', 'startmenuexperiencehost', 'textinputhost'
)

Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class WindowApi {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint message, IntPtr wParam, IntPtr lParam);
}
'@

function Test-NameMatch {
    param([string]$Name, [string[]]$Candidates)
    foreach ($Candidate in $Candidates) {
        if ($Name -eq $Candidate -or $Name.StartsWith("$Candidate-") -or $Name.StartsWith("$Candidate.")) {
            return $true
        }
    }
    return $false
}

function Get-ApplicationWindows {
    $script:FoundWindows = @()
    $Callback = [WindowApi+EnumWindowsProc] {
        param([IntPtr]$Handle, [IntPtr]$Parameter)

        if (-not [WindowApi]::IsWindowVisible($Handle)) { return $true }
        $Length = [WindowApi]::GetWindowTextLength($Handle)
        if ($Length -le 0) { return $true }

        [uint32]$ProcessId = 0
        [void][WindowApi]::GetWindowThreadProcessId($Handle, [ref]$ProcessId)
        if ($ProcessId -eq $PID) { return $true }

        try {
            $Process = Get-Process -Id $ProcessId -ErrorAction Stop
            $Buffer = [Text.StringBuilder]::new($Length + 1)
            [void][WindowApi]::GetWindowText($Handle, $Buffer, $Buffer.Capacity)
            $script:FoundWindows += [pscustomobject]@{
                Handle = $Handle
                Key = $Handle.ToInt64().ToString()
                Process = $Process.ProcessName.ToLowerInvariant()
                Title = $Buffer.ToString()
            }
        } catch {
            # The process may have exited while windows were being enumerated.
        }
        return $true
    }

    [void][WindowApi]::EnumWindows($Callback, [IntPtr]::Zero)
    return $script:FoundWindows
}

$CreatedNew = $false
$Mutex = [Threading.Mutex]::new($true, 'Local\HyprAutoCleanup', [ref]$CreatedNew)
if (-not $CreatedNew) { exit 0 }

$LastActive = @{}
try {
    while ($true) {
        try {
            $Now = [Environment]::TickCount64
            $Foreground = [WindowApi]::GetForegroundWindow()
            $Windows = @(Get-ApplicationWindows)
            $CurrentKeys = [Collections.Generic.HashSet[string]]::new()

            foreach ($Window in $Windows) {
                [void]$CurrentKeys.Add($Window.Key)
                if ($Window.Handle -eq $Foreground) {
                    $LastActive[$Window.Key] = $Now
                    continue
                }
                if (-not $LastActive.ContainsKey($Window.Key)) {
                    $LastActive[$Window.Key] = $Now
                }

                if ((Test-NameMatch $Window.Process $NeverClose) -or
                    (Test-NameMatch $Window.Process $SystemProcesses)) {
                    continue
                }

                $Timeout = if (Test-NameMatch $Window.Process $Browsers) {
                    $BrowserTimeoutSeconds
                } else {
                    $DefaultTimeoutSeconds
                }
                $InactiveSeconds = ($Now - $LastActive[$Window.Key]) / 1000

                if ($InactiveSeconds -ge $Timeout) {
                    # WM_CLOSE lets the application ask to save unsaved work.
                    [void][WindowApi]::PostMessage($Window.Handle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)
                    Write-Output "Closed $($Window.Process): $($Window.Title)"
                    $LastActive.Remove($Window.Key)
                }
            }

            foreach ($Key in @($LastActive.Keys)) {
                if (-not $CurrentKeys.Contains($Key)) { $LastActive.Remove($Key) }
            }
        } catch {
            Write-Error "Window scan failed: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds $CheckIntervalSeconds
    }
} finally {
    $Mutex.ReleaseMutex()
    $Mutex.Dispose()
}
