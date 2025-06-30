#!/usr/bin/env pwsh
# 启动完整 Hanbon 项目脚本

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "         欢迎使用 Hanbon 网站项目           " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 检查项目结构
$frontendPath = "hanbon-vue3-project"
$backendPath = "hanbon_python_backend"

if (!(Test-Path $frontendPath)) {
    Write-Host "错误: 未找到前端项目目录 $frontendPath" -ForegroundColor Red
    exit 1
}

if (!(Test-Path $backendPath)) {
    Write-Host "错误: 未找到后端项目目录 $backendPath" -ForegroundColor Red
    exit 1
}

# 启动后端
Write-Host "`n[1/2] 启动 Python 后端..." -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray

Start-Job -Name "Backend" -ScriptBlock {
    param($backendPath)
    Set-Location $backendPath
    
    # 激活虚拟环境
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
    }
    
    # 启动后端
    Set-Location "src"
    python app.py
} -ArgumentList (Get-Location).Path + "\" + $backendPath

Start-Sleep -Seconds 3

# 启动前端
Write-Host "`n[2/2] 启动 Vue3 前端..." -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray

Set-Location $frontendPath

# 检查是否安装了依赖
if (!(Test-Path "node_modules")) {
    Write-Host "正在安装前端依赖..." -ForegroundColor Yellow
    npm install
}

# 启动前端（在前台运行）
Write-Host "启动前端开发服务器..." -ForegroundColor Green
npm run serve

# 清理后台任务
Write-Host "`n正在关闭后台服务..." -ForegroundColor Yellow
Get-Job | Stop-Job
Get-Job | Remove-Job

Write-Host "项目已关闭" -ForegroundColor Gray 