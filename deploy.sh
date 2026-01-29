#!/bin/bash

# 部署配置
SERVER_IP="122.51.215.20"
SERVER_USER="root"
PROJECT_DIR="/opt/comic-generator"
LOCAL_ARCHIVE="comic-generator.tar.gz"

# 1. 本地打包
echo "Creating local archive..."
tar --exclude='node_modules' \
    --exclude='.venv' \
    --exclude='.git' \
    --exclude='.idea' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.tar.gz' \
    -czf $LOCAL_ARCHIVE .

# 2. 上传到服务器
echo "Uploading archive to $SERVER_IP..."
scp $LOCAL_ARCHIVE $SERVER_USER@$SERVER_IP:/tmp/

# 3. 远程部署
echo "Deploying on remote server..."
ssh $SERVER_USER@$SERVER_IP << EOF
    # 安装 Docker (如果未安装)
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
    fi

    # 准备目录
    mkdir -p $PROJECT_DIR
    
    # 解压文件
    tar -xzf /tmp/$LOCAL_ARCHIVE -C $PROJECT_DIR
    rm /tmp/$LOCAL_ARCHIVE
    
    # 进入目录
    cd $PROJECT_DIR
    
    # 停止旧容器
    docker compose down || true
    
    # 构建并启动新容器
    docker compose up -d --build
    
    # 清理未使用的镜像
    docker image prune -f
    
    echo "Deployment completed!"
    docker compose ps
EOF

# 4. 清理本地文件
rm $LOCAL_ARCHIVE

echo "Done! Visit http://$SERVER_IP"
