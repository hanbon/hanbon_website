# 服务器配置
$servers = @{
    "prod1" = @{
        "name" = "生产服务器1（到期：2024-03）"
        "host" = "121.43.119.166"
        "user" = "root"
        "password" = "Tangrui1002"
    }
    "prod2" = @{
        "name" = "生产服务器2（到期：2024-12）"
        "host" = "112.74.59.41"
        "user" = "root"
        "password" = "Tangrui1002"
    }
}

# 显示服务器选择菜单
function Show-ServerMenu {
    Write-Host "`n=== 选择目标服务器 ===" -ForegroundColor Cyan
    foreach ($key in $servers.Keys) {
        Write-Host "输入 '$key' 选择: $($servers[$key].name) ($($servers[$key].host))" -ForegroundColor Yellow
    }
    Write-Host "=============="
}

# 选择服务器
Show-ServerMenu
$server_choice = Read-Host "请选择服务器"

if (-not $servers.ContainsKey($server_choice)) {
    Write-Host "无效的选择！" -ForegroundColor Red
    exit
}

$selected_server = $servers[$server_choice]
$REMOTE_USER = $selected_server.user
$REMOTE_HOST = $selected_server.host

# 检查是否已经存在 SSH 密钥
if (!(Test-Path "~/.ssh/id_rsa")) {
    Write-Host "生成 SSH 密钥..." -ForegroundColor Yellow
    ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE/.ssh/id_rsa" -N '""'
}

# 上传公钥到服务器
Write-Host "上传公钥到服务器 $($selected_server.name)..." -ForegroundColor Yellow
$pubkey = Get-Content "$env:USERPROFILE/.ssh/id_rsa.pub"

# 创建临时脚本文件
$tempScript = New-TemporaryFile
@"
#!/bin/bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '$pubkey' > ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo 'Setup completed'
"@ | Set-Content -Path $tempScript -Encoding UTF8

# 使用密码认证上传和执行脚本
Write-Host "正在配置服务器..." -ForegroundColor Yellow

# 上传脚本
Write-Host "请输入服务器密码以上传公钥..."
$uploadResult = scp -o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PasswordAuthentication=yes $tempScript "${REMOTE_USER}@${REMOTE_HOST}:/tmp/ssh_setup.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host "上传脚本失败！" -ForegroundColor Red
    exit
}

# 执行脚本
Write-Host "请再次输入服务器密码以执行配置..."
$execResult = ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PasswordAuthentication=yes "${REMOTE_USER}@${REMOTE_HOST}" "bash /tmp/ssh_setup.sh && rm /tmp/ssh_setup.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host "执行脚本失败！" -ForegroundColor Red
    exit
}

# 清理临时文件
Remove-Item $tempScript

# 测试免密登录
Write-Host "测试免密登录..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# 测试连接
$test = ssh -o StrictHostKeyChecking=no "${REMOTE_USER}@${REMOTE_HOST}" "echo 'Success'"

if ($test -eq "Success") {
    Write-Host "免密登录配置成功！" -ForegroundColor Green
} else {
    Write-Host "配置可能有问题，请检查以下内容：" -ForegroundColor Red
    Write-Host "1. 检查本地密钥：" -ForegroundColor Yellow
    Write-Host "   ls $env:USERPROFILE\.ssh\id_rsa*"
    Write-Host "2. 检查服务器配置：" -ForegroundColor Yellow
    Write-Host "   请输入密码以检查服务器配置..."
    ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PasswordAuthentication=yes "${REMOTE_USER}@${REMOTE_HOST}" 'ls -la ~/.ssh/; cat ~/.ssh/authorized_keys'
} 