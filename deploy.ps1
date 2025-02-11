# 服务器配置
$servers = @{
    "prod1" = @{
        "name" = "生产服务器1（到期：2024-03）"
        "host" = "121.43.119.166"
        "user" = "root"
        "domain" = "hanbon.xyz"
        "ssl_path" = "ssl"  # 证书目录
        "os" = "ubuntu"  # 操作系统类型
    }
    "prod2" = @{
        "name" = "生产服务器2（到期：2024-12）"
        "host" = "112.74.59.41"
        "user" = "root"
        "domain" = "hanbon.xyz"
        "ssl_path" = "ssl"  # 证书目录
        "os" = "ubuntu"  # 操作系统类型
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
$DOMAIN_NAME = $selected_server.domain
$REMOTE_PATH = "/opt/hanbon"
$FRONTEND_PATH = ".\hanbon-vue3-project"
$BACKEND_PATH = ".\hanbon_python_backend"

# 显示菜单
function Show-Menu {
    Write-Host "`n=== 部署选项 ===" -ForegroundColor Cyan
    Write-Host "1. 仅更新前端代码" -ForegroundColor Yellow
    Write-Host "2. 仅更新后端代码" -ForegroundColor Yellow
    Write-Host "3. 更新前端和后端代码" -ForegroundColor Yellow
    Write-Host "4. 重启服务" -ForegroundColor Yellow
    Write-Host "5. 配置 SSL 证书" -ForegroundColor Yellow
    Write-Host "6. 首次部署（安装环境）" -ForegroundColor Green
    Write-Host "0. 退出" -ForegroundColor Red
    Write-Host "=============="
}

# 部署前端代码
function Deploy-Frontend {
    Write-Host "`n开始部署前端..." -ForegroundColor Green
    
    # 构建前端项目
    Set-Location $FRONTEND_PATH
    npm install
    npm run build
    Set-Location ..

    # 复制前端构建文件到服务器
    $remote_dest = "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/frontend"
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "rm -rf ${REMOTE_PATH}/frontend/*"
    scp -r "${FRONTEND_PATH}/dist/." $remote_dest

    # 设置权限
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "chown -R www-data:www-data /opt/hanbon/frontend && chmod -R 755 /opt/hanbon/frontend"
    
    Write-Host "前端部署完成！" -ForegroundColor Green
}

# 部署后端代码
function Deploy-Backend {
    Write-Host "`n开始部署后端..." -ForegroundColor Green
    
    # 复制后端文件
    $remote_dest = "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/backend"
    
    # 确保目标目录存在
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p ${REMOTE_PATH}/backend"
    
    # 复制源代码文件
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "rm -rf ${REMOTE_PATH}/backend/src"
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "rm -rf ${REMOTE_PATH}/backend/config"
    scp -r "${BACKEND_PATH}/src" $remote_dest/
    scp -r "${BACKEND_PATH}/config" $remote_dest/
    
    # 复制其他必要文件（如果存在）
    if (Test-Path "${BACKEND_PATH}/requirements.txt") {
        scp "${BACKEND_PATH}/requirements.txt" $remote_dest/
    }
    
    # 设置正确的权限
    ssh "${REMOTE_USER}@${REMOTE_HOST}" @'
cd /opt/hanbon/backend
chown -R root:root .
chmod -R 755 .

# 安装新的依赖（如果有）
source venv/bin/activate
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 停止现有的服务
pkill -f "uvicorn" || true
sleep 2

# 设置环境变量并启动服务
export ENV=production
export PYTHONPATH=/opt/hanbon/backend
nohup uvicorn src.sse:app --host 0.0.0.0 --port 7999  > app.log 2>&1 &

# 显示启动日志
tail -300f app.log
sleep 5
'@
    
    Write-Host "后端部署完成！" -ForegroundColor Green
}

# 重启服务
function Restart-Services {
    Write-Host "`n开始重启服务..." -ForegroundColor Green
    
    $remote_commands = @'
# 重启 Nginx
/usr/sbin/nginx -t && (killall nginx; /usr/sbin/nginx)

# 重启后端服务
cd /opt/hanbon/backend
source venv/bin/activate
pkill -f "uvicorn" || true
sleep 2

# 设置环境变量并启动服务
export ENV=production
export PYTHONPATH=/opt/hanbon/backend
nohup python -m uvicorn src.sse:app --host 0.0.0.0 --port 7999 --log-level debug > app.log 2>&1 &

# 显示启动日志
tail -f app.log &
sleep 5
'@ -replace "`r`n", "`n"

    ssh "${REMOTE_USER}@${REMOTE_HOST}" $remote_commands
    
    Write-Host "服务重启完成！" -ForegroundColor Green
}

# 配置 SSL 证书
function Configure-SSL {
    Write-Host "`n开始配置 SSL 证书..." -ForegroundColor Green
    
    # 创建证书目录
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p /etc/nginx/ssl"
    
    # 复制证书文件
    $ssl_path = $selected_server.ssl_path
    scp "./${ssl_path}/hanbon.xyz_bundle.pem" "${REMOTE_USER}@${REMOTE_HOST}:/etc/nginx/ssl/fullchain.pem"
    scp "./${ssl_path}/hanbon.xyz.key" "${REMOTE_USER}@${REMOTE_HOST}:/etc/nginx/ssl/privkey.key"
    
    # 配置 Nginx SSL
    $ssl_config = @"
# HTTP - 重定向到 HTTPS
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    return 301 https://`$server_name`$request_uri;
}

# HTTPS
server {
    listen 443 ssl;  # 使用新的 http2 配置方式
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.key;
    
    # 支持所有版本的 TLS
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers on;
    
    # SSL 会话缓存 - 确保大小一致
    ssl_session_cache shared:SSL:10m;  # 确保与主配置一致
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # 安全头部
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;

    access_log /var/log/nginx/hanbon_access.log;
    error_log /var/log/nginx/hanbon_error.log;

    # 前端文件
    location / {
        root /opt/hanbon/frontend;
        index index.html;
        try_files `$uri `$uri/ /index.html;
        
        # 添加安全头部
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options SAMEORIGIN;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:7999/;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        
        # 添加安全头部
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options SAMEORIGIN;
    }
}
"@ -replace "`r`n", "`n"

    # 更新 Nginx 配置
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "echo '$ssl_config' > /etc/nginx/conf.d/hanbon.conf"
    
    # 设置证书权限并重启 Nginx
    ssh "${REMOTE_USER}@${REMOTE_HOST}" @'
chmod 644 /etc/nginx/ssl/fullchain.pem
chmod 600 /etc/nginx/ssl/privkey.key
/usr/sbin/nginx -t && (killall nginx; /usr/sbin/nginx)
'@

    Write-Host "SSL 证书配置完成！" -ForegroundColor Green
}

# 首次部署函数
function Initial-Deploy {
    Write-Host "`n开始首次部署..." -ForegroundColor Green
    
    $setup_commands = @'
# 等待任何正在运行的 apt 进程完成
while ps aux | grep -i apt | grep -v grep > /dev/null; do
    echo "等待其他 apt 进程完成..."
    sleep 5
done

# 清理可能的锁文件
rm -f /var/lib/dpkg/lock*
rm -f /var/lib/apt/lists/lock
rm -f /var/cache/apt/archives/lock

# 修复 dpkg
dpkg --configure -a

# 更新系统包
apt-get update
apt-get upgrade -y

# 卸载已存在的 nginx
apt-get remove -y nginx nginx-common nginx-full
apt-get autoremove -y
apt-get autoclean

# 清理旧的 nginx 目录
rm -rf /etc/nginx
rm -rf /var/log/nginx
rm -rf /var/lib/nginx
rm -rf /usr/share/nginx

# 安装必要的软件包
apt-get install -y python3 python3-pip python3.12-venv nginx

# 确保 mime.types 文件存在
if [ ! -f "/etc/nginx/mime.types" ]; then
    # 如果目录不存在则创建
    mkdir -p /etc/nginx
    
    # 创建基本的 mime.types 文件
    cat > /etc/nginx/mime.types << 'ENDMIME'
types {
    text/html                                        html htm shtml;
    text/css                                         css;
    text/xml                                         xml;
    image/gif                                        gif;
    image/jpeg                                       jpeg jpg;
    application/javascript                           js;
    application/atom+xml                             atom;
    application/rss+xml                             rss;
    text/plain                                       txt;
    image/png                                        png;
    image/svg+xml                                    svg svgz;
    image/x-icon                                     ico;
    application/pdf                                  pdf;
    application/x-font-ttf                           ttf;
    application/x-font-woff                          woff;
    application/json                                 json;
}
ENDMIME
fi

# 创建必要的目录
mkdir -p /opt/hanbon/frontend
mkdir -p /opt/hanbon/backend
mkdir -p /etc/nginx/ssl
mkdir -p /etc/nginx/conf.d
mkdir -p /var/log/nginx

# 安装 Python 虚拟环境
cd /opt/hanbon/backend
python3 -m venv venv --without-pip
curl -sS https://bootstrap.pypa.io/get-pip.py | ./venv/bin/python3

source venv/bin/activate
# 使用国内镜像源
./venv/bin/pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
./venv/bin/pip install --upgrade pip

# 配置 Nginx
cat > /etc/nginx/nginx.conf << 'ENDNGINX'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 768;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;

    include /etc/nginx/conf.d/*.conf;
}
ENDNGINX

# 配置防火墙
if command -v ufw > /dev/null; then
    ufw allow 80 || true
    ufw allow 443 || true
    ufw allow 22 || true
fi

# 设置目录权限
chown -R www-data:www-data /opt/hanbon/frontend
chmod -R 755 /opt/hanbon/frontend
chown -R www-data:www-data /var/log/nginx
chmod -R 755 /var/log/nginx

# 启动 Nginx（使用 service 命令，因为是 Ubuntu 24.04）
/usr/sbin/nginx

echo "Initial setup completed"
'@ -replace "`r`n", "`n"

    # 执行服务器端配置
    Write-Host "配置服务器环境..." -ForegroundColor Yellow
    ssh "${REMOTE_USER}@${REMOTE_HOST}" $setup_commands

    # 部署前端代码
    Write-Host "部署前端代码..." -ForegroundColor Yellow
    Deploy-Frontend

    # 部署后端代码
    Write-Host "部署后端代码..." -ForegroundColor Yellow
    Deploy-Backend

    # 配置 SSL
    Write-Host "配置 SSL..." -ForegroundColor Yellow
    Configure-SSL

    Write-Host "`n首次部署完成！" -ForegroundColor Green
    Write-Host "你现在可以通过以下地址访问网站：" -ForegroundColor Cyan
    Write-Host "HTTPS: https://$DOMAIN_NAME" -ForegroundColor Cyan
    Write-Host "HTTP:  http://$DOMAIN_NAME  (会自动重定向到 HTTPS)" -ForegroundColor Cyan
}

# 主循环
while ($true) {
    Show-Menu
    $choice = Read-Host "请选择操作"
    
    switch ($choice) {
        "1" { Deploy-Frontend }
        "2" { Deploy-Backend }
        "3" { 
            Deploy-Frontend
            Deploy-Backend
        }
        "4" { Restart-Services }
        "5" { Configure-SSL }
        "6" { Initial-Deploy }
        "0" { 
            Write-Host "`n退出程序..." -ForegroundColor Yellow
            exit 
        }
        default { Write-Host "`n无效的选择，请重试" -ForegroundColor Red }
    }
} 