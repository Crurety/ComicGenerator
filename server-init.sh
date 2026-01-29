#!/bin/bash

# 服务器初始化脚本
# 请在服务器上运行此脚本以准备环境
# 使用方法: bash server-init.sh

set -e

PROJECT_DIR="/opt/comic-generator"

echo "Initializing server environment..."

# 1. 检查并安装 Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    # 启动 Docker
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
else
    echo "Docker is already installed."
fi

# 2. 创建目录
echo "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

# 3. 设置 SSH 目录权限 (确保 SSH private key auth 能正常工作)
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

echo "
Server initialization completed!

Next steps:
1. Generate SSH Key Pair locally on your Windows machine:
   ssh-keygen -t ed25519 -C \"github-actions-deploy\"

2. Copy the public key content (id_ed25519.pub) into ~/.ssh/authorized_keys on this server:
   echo \"YOUR_PUBLIC_KEY_CONTENT\" >> ~/.ssh/authorized_keys

3. Copy the private key content (id_ed25519) to GitHub Repository Secrets as 'SERVER_SSH_KEY'.
"
