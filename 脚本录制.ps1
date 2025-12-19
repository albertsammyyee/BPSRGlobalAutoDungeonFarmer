$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "`n需要管理员权限才能继续，将弹出 UAC 提示..." -ForegroundColor Cyan
    Write-Host "提示：原窗口将在 2 秒后关闭，新管理员窗口会启动" -ForegroundColor Cyan
    Start-Sleep -Seconds 1  # 等待1 秒，让用户看清提示
    
    $arguments = "-File `"$($MyInvocation.MyCommand.Definition)`""
    Start-Process powershell.exe -Verb RunAs -ArgumentList $arguments
    exit
}

# 以下是管理员权限的核心逻辑
Write-Host "`n? 已获取管理员权限，开始执行操作..." -ForegroundColor Green
# （你的核心代码，比如创建虚拟环境、安装依赖等）
$scriptPath = $PSScriptRoot
Write-Host "当前脚本目录: $scriptPath"

# 拼接虚拟环境中Python的绝对路径
$pythonPath = Join-Path -Path $scriptPath -ChildPath "venv\Scripts\python.exe"
# 拼接Main.py的绝对路径
$mainScript = Join-Path -Path $scriptPath -ChildPath "com\recorder.py"
& $pythonPath $mainScript
# 最后添加暂停，避免执行完直接关闭
Write-Host "`n? 操作完成！" -ForegroundColor Green
pause


pause