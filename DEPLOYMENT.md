# 部署指南

本文档介绍如何部署飞书 AI 机器人到生产环境。

---

## 📋 部署前准备

### 1. 系统要求

- Python 3.9+
- Linux/Windows Server
- 公网 IP 或内网穿透工具

### 2. 飞书应用配置

1. 在飞书开放平台创建应用
2. 获取 `App ID` 和 `App Secret`
3. 配置机器人能力
4. 配置事件订阅 Webhook URL

---

## 🚀 部署方式

### 方式一：直接部署（有公网IP）

如果你的服务器有公网 IP，可以直接部署：

```bash
# 1. 克隆项目
git clone https://github.com/Luys521/JiaWei_bot.git
cd JiaWei_bot

# 2. 安装依赖
python -m venv venv
source venv/bin/activate
pip install -e .

# 3. 配置环境变量
cp configs/.env.example .env
vim .env

# 4. 启动服务
python -m feishu_ai_bot.server
```

**飞书 Webhook 配置：**
```
http://your-server-ip:8080/webhook/event
```

---

### 方式二：使用内网穿透（推荐）

如果你的服务器没有公网 IP，需要使用内网穿透工具（如 frp）。

#### 步骤 1：安装 frp

**下载 frp：**
```bash
# 访问 https://github.com/fatedier/frp/releases
# 下载适合你系统的版本

# Linux 示例
wget https://github.com/fatedier/frp/releases/download/v0.52.0/frp_0.52.0_linux_amd64.tar.gz
tar -xzf frp_0.52.0_linux_amd64.tar.gz
cd frp_0.52.0_linux_amd64
```

#### 步骤 2：配置 frp 服务端（公网服务器）

创建 `frps.ini`：

```ini
[common]
bind_port = 7000
authentication_method = token
token = your_secure_token_here

# 可选：Dashboard
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = your_dashboard_password
```

启动 frp 服务端：
```bash
./frps -c frps.ini
```

#### 步骤 3：配置 frp 客户端（内网服务器）

创建 `frpc.ini`：

```ini
[common]
server_addr = your_public_server_ip
server_port = 7000
authentication_method = token
token = your_secure_token_here

[feishu_webhook]
type = http
local_ip = 127.0.0.1
local_port = 8080
custom_domains = your_domain.com
# 或使用子域名
subdomain = feishu
```

启动 frp 客户端：
```bash
./frpc -c frpc.ini
```

#### 步骤 4：配置飞书 Webhook

**使用域名：**
```
http://your_domain.com/webhook/event
```

**使用子域名：**
```
http://feishu.your_frp_server.com/webhook/event
```

---

### 方式三：使用 systemd（生产环境推荐）

#### 1. 创建应用服务

创建 `/etc/systemd/system/feishu-bot.service`：

```ini
[Unit]
Description=Feishu AI Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/JiaWei_bot
Environment="PATH=/path/to/JiaWei_bot/venv/bin"
ExecStart=/path/to/JiaWei_bot/venv/bin/python -m feishu_ai_bot.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 创建 frp 服务（如需要）

创建 `/etc/systemd/system/frpc.service`：

```ini
[Unit]
Description=FRP Client
After=network.target

[Service]
Type=simple
User=your_user
ExecStart=/path/to/frp/frpc -c /path/to/frp/frpc.ini
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. 启动服务

```bash
# 启动应用
sudo systemctl daemon-reload
sudo systemctl start feishu-bot
sudo systemctl enable feishu-bot

# 启动 frp（如需要）
sudo systemctl start frpc
sudo systemctl enable frpc

# 查看状态
sudo systemctl status feishu-bot
sudo systemctl status frpc
```

---

### 方式四：使用 Docker

#### 1. 构建镜像

```bash
docker build -t feishu-ai-bot .
```

#### 2. 运行容器

```bash
docker run -d \
  --name feishu-bot \
  -p 8080:8080 \
  --env-file .env \
  --restart unless-stopped \
  feishu-ai-bot
```

#### 3. 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  feishu-bot:
    build: .
    container_name: feishu-bot
    ports:
      - "8080:8080"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

启动：
```bash
docker-compose up -d
```

---

## 🔒 安全配置

### 1. 配置防火墙

```bash
# 只开放必要端口
sudo ufw allow 8080/tcp  # 应用端口
sudo ufw allow 7000/tcp  # frp 端口（如使用）
sudo ufw enable
```

### 2. 使用 HTTPS

建议使用 Nginx 反向代理并配置 SSL 证书：

```nginx
server {
    listen 443 ssl;
    server_name your_domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 环境变量安全

- ✅ 使用强密码
- ✅ 定期更换 API 密钥
- ✅ 不要将 `.env` 提交到 Git
- ✅ 限制文件权限：`chmod 600 .env`

---

## 📊 监控和日志

### 查看日志

```bash
# 应用日志
tail -f logs/bot.log

# systemd 日志
sudo journalctl -u feishu-bot -f

# Docker 日志
docker logs -f feishu-bot
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8080/health

# 检查统计信息
curl http://localhost:8080/stats
```

---

## 🔧 故障排查

### 问题 1：Webhook 接收不到消息

**检查项：**
- [ ] 服务是否正常运行
- [ ] 端口是否开放
- [ ] frp 是否正常连接
- [ ] 飞书 Webhook URL 是否正确
- [ ] 飞书应用权限是否配置

**调试命令：**
```bash
# 测试本地服务
curl -X POST http://localhost:8080/webhook/event \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# 测试 frp 穿透
curl http://your_domain.com/health
```

### 问题 2：服务启动失败

**检查项：**
- [ ] Python 版本是否正确
- [ ] 依赖是否安装完整
- [ ] 环境变量是否配置
- [ ] 端口是否被占用

**调试命令：**
```bash
# 检查端口占用
netstat -tlnp | grep 8080

# 手动启动查看错误
python -m feishu_ai_bot.server
```

### 问题 3：frp 连接失败

**检查项：**
- [ ] 服务端是否运行
- [ ] token 是否一致
- [ ] 网络是否通畅
- [ ] 防火墙是否开放端口

**调试命令：**
```bash
# 测试服务端连接
telnet your_server_ip 7000

# 查看 frp 日志
./frpc -c frpc.ini -L debug
```

---

## 📝 配置示例

### 完整的 .env 示例

```env
# 飞书应用配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxx
FEISHU_BOT_OPEN_ID=ou_xxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxx

# AI 服务配置
AI_PROVIDER=deepseek
AI_API_KEY=sk-xxxxxxxxxxxxx
AI_API_BASE=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
WORKSPACE_DIR=/path/to/workspace

# 可选：OpenClaw 配置
OPENCLAW_ENABLED=true
OPENCLAW_API_URL=http://localhost:8000
OPENCLAW_TOKEN=your_openclaw_token

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

---

## 🎯 生产环境检查清单

部署前请确认：

- [ ] 环境变量已正确配置
- [ ] 所有密钥使用强密码
- [ ] 防火墙规则已配置
- [ ] SSL 证书已配置（如使用 HTTPS）
- [ ] 日志目录有写入权限
- [ ] 服务设置为自动重启
- [ ] 监控和告警已配置
- [ ] 备份策略已制定

---

## 📞 获取帮助

如遇到问题：

1. 查看日志文件
2. 检查 [GitHub Issues](https://github.com/Luys521/JiaWei_bot/issues)
3. 提交新的 Issue

---

**最后更新**: 2026-02-10
