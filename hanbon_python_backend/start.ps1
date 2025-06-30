#!/usr/bin/env pwsh
# 启动 Python 后端脚本

Write-Host "正在启动 Hanbon Python 后端..." -ForegroundColor Green

# 检查是否在虚拟环境中
if ($env:VIRTUAL_ENV) {
    Write-Host "已在虚拟环境中: $env:VIRTUAL_ENV" -ForegroundColor Yellow
} else {
    # 检查是否存在虚拟环境
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Host "激活虚拟环境..." -ForegroundColor Yellow
        & "venv\Scripts\Activate.ps1"
    } else {
        Write-Host "未找到虚拟环境，请先创建虚拟环境" -ForegroundColor Red
        Write-Host "运行: python -m venv venv" -ForegroundColor Yellow
        exit 1
    }
}

# 检查 Python 版本
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Python" -ForegroundColor Red
    exit 1
}

Write-Host "Python 版本: $pythonVersion" -ForegroundColor Yellow

# 安装依赖（如果需要）
if (Test-Path "requirements.txt") {
    Write-Host "检查并安装 Python 依赖..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 启动 Flask 应用
Write-Host "启动 Flask 后端服务器..." -ForegroundColor Green
Set-Location "src"
python app.py 