# Comic Generator Deployment Guide

## 🚀 GitHub Actions 自动部署 (推荐)

本项目已配置 GitHub Actions，只需推送代码到 `main` 分支即可自动部署。

### 1. 准备工作

#### 生成 SSH 密钥对
在本地 PowerShell 中运行：
```powershell
ssh-keygen -t ed25519 -C "github-actions-deploy" -f id_ed25519 -N ""
```
这将生成两个文件：
- `id_ed25519` (私钥 - 放入 GitHub Secrets)
- `id_ed25519.pub` (公钥 - 放入服务器)

#### 配置 GitHub Secrets
进入 GitHub 仓库 -> Settings -> Secrets and variables -> Actions -> **New repository secret**，添加以下变量：

| Secret 名称 | 值说明 |
|------------|--------|
| `SERVER_HOST` | `122.51.215.20` |
| `SERVER_USER` | `root` |
| `SERVER_SSH_KEY` | `id_ed25519` 文件的完整内容 |
| `GEMINI_API_KEY` | 你的 Gemini API 密钥 |
| `MIDJOURNEY_API_KEY` | (可选) Midjourney API 密钥 |
| `SECRET_KEY` | Flask Secret Key (随机字符串) |
| `JWT_SECRET_KEY` | JWT Secret Key (随机字符串) |

### 2. 服务器初始化 (仅需一次)

将 `server-init.sh` 上传到服务器并运行，或者手动执行以下命令：

1. **登录服务器**
   ```bash
   ssh root@122.51.215.20
   ```

2. **添加公钥**
   将本地 `id_ed25519.pub` 的内容复制，然后在服务器上运行：
   ```bash
   mkdir -p ~/.ssh
   echo "粘贴你的公钥内容在这里" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

### 3. 触发部署

只需提交代码并推送到 main 分支：
```bash
git add .
git commit -m "Trigger deployment"
git push origin main
```

可以在 GitHub 仓库的 **Actions** 标签页查看部署进度。

---

## 🛠️ 手动部署 (备用方案)

如果自动部署失败，可以使用原有脚本：

```powershell
./deploy.sh
```

## 故障排查

- **Docker Permission Denied**: 确保 SSH 用户有 docker 权限 (root 用户默认有)。
- **Connection Timeout**: 检查服务器防火墙是否允许 22 端口 (SSH)。
- **Secret Key Error**: 确保 GitHub Secrets 中设置了所有必要的 Key。
