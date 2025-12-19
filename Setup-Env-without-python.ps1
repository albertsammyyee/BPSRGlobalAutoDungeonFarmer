# 定义虚拟环境名称
$venvName = "venv"
mv ./venv_back ./venv
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
    