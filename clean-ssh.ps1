# 清理特定 IP 的 known_hosts 记录
$IP_TO_CLEAN = "112.74.59.41"
$KNOWN_HOSTS = "$env:USERPROFILE\.ssh\known_hosts"

# 备份原文件
if (Test-Path $KNOWN_HOSTS) {
    Copy-Item $KNOWN_HOSTS "$KNOWN_HOSTS.bak"
    
    # 删除包含特定 IP 的行
    $content = Get-Content $KNOWN_HOSTS | Where-Object { $_ -notmatch $IP_TO_CLEAN }
    Set-Content $KNOWN_HOSTS $content
    
    Write-Host "已清理 $IP_TO_CLEAN 的旧密钥记录" -ForegroundColor Green
} else {
    Write-Host "known_hosts 文件不存在，无需清理" -ForegroundColor Yellow
} 