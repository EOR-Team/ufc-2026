# Nginx HTTPS 代理配置指南

> 本文档提供将前端开发服务器配置为 HTTPS 访问的完整指南，以解决跨域麦克风访问问题

---

## 概述

### 问题背景
在浏览器安全策略下，**麦克风访问** 要求页面通过 **HTTPS** 协议加载。开发环境通常使用 HTTP，导致麦克风权限请求失败。

### 解决方案
使用 **Nginx 反向代理** 将本地 HTTP 开发服务器（localhost:5173）暴露为 HTTPS 服务（localhost:9000），从而启用跨域麦克风访问。

---

## 配置文件

### 1. Nginx 主配置文件
**位置**: `/home/n1ghts4kura/Desktop/ufc-2026/nginx.example.conf`（项目根目录）

**核心功能**：
- 监听 HTTPS 端口 `9000`，自动将 HTTP 请求重定向到 HTTPS
- 代理所有请求到 Vite 开发服务器 `localhost:5173`
- 支持 Vue Router history 模式
- 包含 WebSocket 代理，支持 Vite 热模块替换（HMR）
- 可选的后端 API 代理（注释状态）

### 2. SSL 证书生成脚本
**位置**: `/home/n1ghts4kura/Desktop/ufc-2026/generate-ssl-cert.sh`

**功能**：
- 自动创建自签名 SSL 证书（有效期 365 天）
- 设置正确的文件权限（密钥 600，证书 644）
- 支持 `localhost` 和 `127.0.0.1` 域名

**重要提示**：
- 脚本使用 `sudo` 运行，`$HOME` 环境变量会变为 `/root`
- **必须编辑脚本中的路径**：将 `/home/n1ghts4kura` 替换为您的实际主目录路径
- 路径定义在脚本第 16 行：`SSL_DIR="/home/n1ghts4kura/ssl"`

---

## 安装与配置步骤

### 步骤 0：准备配置文件

1. **复制示例配置文件**：
   ```bash
   cd /home/n1ghts4kura/Desktop/ufc-2026
   cp nginx.example.conf nginx.conf
   ```

2. **编辑 nginx.conf**：
   - 打开 `nginx.conf`
   - 找到第 41-42 行的 `ssl_certificate` 和 `ssl_certificate_key` 配置
   - 将 `/home/n1ghts4kura` 替换为您的实际主目录路径
   - 保存文件

### 步骤 2：生成 SSL 证书

**重要**：在执行前，必须先编辑脚本中的路径：
1. 打开 `generate-ssl-cert.sh`
2. 将第 16 行的 `/home/n1ghts4kura` 替换为您的实际主目录路径
3. 保存文件

```bash
# 切换到项目根目录
cd /home/n1ghts4kura/Desktop/ufc-2026

# 添加执行权限
chmod +x generate-ssl-cert.sh

# 执行生成脚本（需要 sudo 权限）
sudo ./generate-ssl-cert.sh
```

**输出示例**：
```
Generating self-signed SSL certificate for HTTPS...
This certificate will be valid for 365 days.
Creating SSL directory: $HOME/ssl
SSL certificate generated successfully!
Key file: $HOME/ssl/selfsigned.key
Cert file: $HOME/selfsigned.crt
```

### 步骤 3：安装 Nginx（如未安装）
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx -y

# Fedora/RHEL/CentOS
sudo dnf install nginx -y
```

### 步骤 4：验证配置语法
```bash
# 测试配置文件语法
sudo nginx -c /home/n1ghts4kura/Desktop/ufc-2026/nginx.conf -t

# 预期输出
nginx: the configuration file /home/n1ghts4kura/Desktop/ufc-2026/nginx.conf syntax is ok
nginx: configuration file /home/n1ghts4kura/Desktop/ufc-2026/nginx.conf test is successful
```

### 步骤 5：启动 Nginx 服务
```bash
# 启动 Nginx
sudo nginx -c /home/n1ghts4kura/Desktop/ufc-2026/nginx.conf

# 检查运行状态
ps aux | grep nginx

# 查看监听端口
sudo netstat -tlnp | grep :9000
```

### 步骤 6：启动前端开发服务器
```bash
# 切换到前端目录
cd frontend

# 启动 Vite 开发服务器
npm run dev

# 验证 Vite 运行在 http://localhost:5173
```

---

## 使用方式

### 访问应用
1. 打开浏览器访问：**https://localhost:9000**
2. 浏览器将显示 **安全警告**（自签名证书的正常现象）
3. 点击 **"高级"** → **"继续前往 localhost (不安全)"**
4. 地址栏显示 **🔒 HTTPS 安全连接** 图标

### 麦克风权限测试
1. 点击设置页面 → **"请求麦克风权限"** 按钮
2. 浏览器应正常弹出麦克风权限请求对话框
3. 授权后即可使用语音功能

### 路由测试
- 访问 `https://localhost:9000/settings`（应正常工作，无 `#` 符号）
- 使用底部导航栏切换页面（应保持历史记录）
- 浏览器后退/前进按钮应正常工作

---

## 配置详解

### MIME 类型配置说明
配置文件使用内置的最小化 MIME 类型定义。如果您使用自定义安装的 Nginx，可以：

1. **使用自定义 mime.types 文件**：在 `http` 块开头添加
   ```nginx
   include /path/to/your/nginx/conf/mime.types;
   ```
2. **使用内置定义**：保留当前的 `types` 块定义

### Nginx 配置文件结构
```nginx
# HTTP 重定向（端口 80）
server {
    listen 80;
    return 301 https://$server_name:9000$request_uri;
}

# HTTPS 主服务器（端口 9000）
server {
    listen 9000 ssl;
    # IMPORTANT: Replace /home/n1ghts4kura with your own home directory path
    ssl_certificate /home/n1ghts4kura/ssl/selfsigned.crt;
    ssl_certificate_key /home/n1ghts4kura/ssl/selfsigned.key;

    # 代理到 Vite 开发服务器
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 历史模式回退（由 Vite 处理）
    error_page 404 /index.html;
}
```

### 前端路由配置
**文件**: `frontend/src/router/index.js`
```javascript
// 当前已使用 history 模式（无需修改）
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),  // ✅ 已经是 history 模式
  routes: [...]
})
```

---

## 故障排除

### 常见问题与解决方案

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| **Nginx 启动失败** | 端口冲突或配置文件错误 | `sudo nginx -c nginx.example.conf -t` 检查语法 |
| **SSL 证书错误** | 证书文件权限或路径错误 | 检查 `$HOME/ssl/` 目录权限，重新生成证书 |
| **代理无法连接** | Vite 服务器未运行 | 确认 `npm run dev` 正在运行，端口 5173 可访问 |
| **麦克风仍不可用** | 仍通过 HTTP 访问 | 确保使用 **https://** 而非 http:// |
| **浏览器安全警告** | 自签名证书 | 接受警告，或添加证书到系统信任列表 |
| **路由 404 错误** | History 模式配置问题 | 确认 Vite 运行，代理配置正确 |

### MIME 类型配置（自定义 Nginx 安装）

如果您使用自定义编译安装的 Nginx，标准路径 `/etc/nginx/mime.types` 可能不存在。解决方案：

**方案 A：使用自定义 mime.types 文件**
1. 找到您的 Nginx 安装目录中的 `mime.types` 文件
   ```bash
   find ~ -name "mime.types" 2>/dev/null | grep nginx
   ```
2. 在 `nginx.conf` 中添加包含指令：
   ```nginx
   include /home/n1ghts4kura/global_nginx/conf/mime.types;
   ```
   （将路径替换为您的实际路径）

**方案 B：使用内置最小化 MIME 类型**
如果找不到 `mime.types` 文件，使用配置文件中的内置 `types` 定义。

**验证方法**：
```bash
# 测试配置文件语法
sudo nginx -c nginx.conf -t
# 应显示 "syntax is ok"
```

### 端口冲突处理
如果端口 9000 已被占用，可修改 `nginx.example.conf`：
```nginx
# 修改监听端口（如改为 9001）
server {
    listen 9001 ssl;  # 改为其他端口
    # ... 其他配置保持不变
}
```

### 证书信任（可选）
如需避免浏览器警告，可将证书添加到系统信任列表：

**Linux**:
```bash
# 复制证书到系统证书目录
sudo cp $HOME/ssl/selfsigned.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

**macOS**:
```bash
# 打开钥匙串访问
open $HOME/ssl/selfsigned.crt
# 将证书添加到"系统"钥匙串，设置为"始终信任"
```

**Windows**:
1. 双击 `selfsigned.crt` 文件
2. 点击"安装证书"
3. 选择"本地计算机" → "将证书放入以下存储" → "受信任的根证书颁发机构"

---

## 生产环境注意事项

### 与开发环境的区别
1. **Vite 构建产物**: 生产环境使用 `npm run build` 生成的静态文件
2. **Nginx 配置调整**: 需要取消注释静态文件服务部分
3. **SSL 证书**: 生产环境应使用受信任的 CA 签发证书（如 Let's Encrypt）

### 生产配置示例
```nginx
# 静态文件服务（取消注释）
# root /home/n1ghts4kura/Desktop/ufc-2026/frontend/dist;
# index index.html;

# History 模式处理（生产环境必需）
location / {
    # try_files $uri $uri/ /index.html;  # 取消注释
}
```

---

## 相关文件

| 文件 | 用途 | 位置 |
|------|------|------|
| `nginx.example.conf` | Nginx 主配置文件 | 项目根目录 |
| `generate-ssl-cert.sh` | SSL 证书生成脚本 | 项目根目录 |
| `router/index.js` | Vue Router 配置 | `frontend/src/router/` |
| `vite.config.js` | Vite 构建配置 | `frontend/` |

---

## 版本历史

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-02-26 | v1.0.0 | 初始版本，包含完整配置指南 |
| 2026-02-26 | - | 创建配置文件，解决跨域麦克风访问问题 |

---

## 参考链接

1. [Nginx 官方文档](https://nginx.org/en/docs/)
2. [Vue Router History 模式](https://router.vuejs.org/guide/essentials/history-mode.html)
3. [浏览器安全策略 - getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia#security)
4. [自签名 SSL 证书创建](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx)
