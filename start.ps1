# Check for admin privileges
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "`nThis script requires administrator privileges. Relaunching with elevated permissions..." -ForegroundColor Cyan
    Write-Host "Please confirm the UAC prompt. If the window closes, relaunch manually as administrator." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    
    $arguments = "-File `"$($MyInvocation.MyCommand.Definition)`""
    Start-Process powershell.exe -Verb RunAs -ArgumentList $arguments
    exit
}

# Admin confirmed
Write-Host "`n[+] Administrator privileges granted. Launching script..." -ForegroundColor Green

# Get script path
$scriptPath = $PSScriptRoot
Write-Host "Current script directory: $scriptPath"

# Build Python executable path
$pythonPath = Join-Path -Path $scriptPath -ChildPath "venv\Scripts\python.exe"
# Build path to main Python script
$mainScript = Join-Path -Path $scriptPath -ChildPath "com\Main.py"

# Run the main Python script
& $pythonPath $mainScript

Write-Host "`n[+] Script finished." -ForegroundColor Green
pause
