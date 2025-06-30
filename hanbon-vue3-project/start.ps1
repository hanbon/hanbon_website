#!/usr/bin/env pwsh
# 启动 Vue3 项目脚本

Write-Host "正在启动 Hanbon Vue3 项目..." -ForegroundColor Green

# 检查是否安装了 Node.js
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Node.js，请先安装 Node.js" -ForegroundColor Red
    exit 1
}

Write-Host "Node.js 版本: $nodeVersion" -ForegroundColor Yellow

# 检查是否安装了依赖
if (!(Test-Path "node_modules")) {
    Write-Host "未找到 node_modules，正在安装依赖..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败" -ForegroundColor Red
        exit 1
    }
}

# 启动开发服务器
Write-Host "启动开发服务器..." -ForegroundColor Green
npm run serve 