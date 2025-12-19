# 定义虚拟环境名称
$venvName = "venv"

# 检查 Python 是否安装
try {
    python --version 2>&1 | Out-Null
} catch {
    Write-Error "未找到 Python 环境，请先安装 Python 并添加到系统 PATH"
    pause
    exit 1
}

# 检查 requirements.txt 是否存在
if (-not (Test-Path "requirements.txt")) {
    Write-Error "当前目录未找到 requirements.txt 文件"
    pause
    exit 1
}

# 创建虚拟环境
Write-Host "正在创建虚拟环境 $venvName..."
python -m venv $venvName

if (-not (Test-Path "$venvName\Scripts\Activate.ps1")) {
    Write-Error "虚拟环境创建失败"
    pause
    exit 1
}

# 激活虚拟环境并安装依赖
Write-Host "正在安装依赖包..."
& "$venvName\Scripts\Activate.ps1"

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

if ($LASTEXITCODE -ne 0) {
    Write-Error "依赖包安装失败"
    pause
    exit 1
}

# 退出虚拟环境
deactivate

Write-Host "`n环境配置完成！"
Write-Host "激活虚拟环境的命令：.\\$venvName\Scripts\Activate.ps1"
pause
    