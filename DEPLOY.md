# Comic Generator Deployment Guide

## Prerequisites
- A Windows machine with PowerShell.
- OpenSSH Client installed (default on Windows 10/11).
- Server credentials (IP, Username, Password).

## Deployment Steps

1.  **Open PowerShell** in the project root directory: `d:\Project\PycharmProjects\ComicGenerator`

2.  **Run the deployment script**:
    The script will compress your project, upload it to the server, and build the Docker containers remotely.

    Since we cannot automate password input securely without extra tools, you will be prompted to enter your server password twice:
    - Once for `scp` (file upload).
    - Once for `ssh` (remote execution).

    Run the following command:

    ```powershell
    # Windows PowerShell Deployment Script
    $ServerIP = "122.51.215.20"
    $User = "root"
    $RemotePath = "/opt/comic-generator"
    $ArchiveName = "comic-generator.tar.gz"

    Write-Host "1. Compressing project files..."
    tar --exclude='node_modules' --exclude='.venv' --exclude='.git' --exclude='.idea' --exclude='__pycache__' --exclude='*.pyc' --exclude='*.tar.gz' -czf $ArchiveName .

    Write-Host "2. Uploading to server (Please enter password when prompted)..."
    scp $ArchiveName ${User}@${ServerIP}:/tmp/

    Write-Host "3. Executing remote deployment (Please enter password when prompted)..."
    ssh ${User}@${ServerIP} "
        # Install Docker if missing
        if ! command -v docker &> /dev/null; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
        fi
        
        # Prepare directory
        mkdir -p $RemotePath
        tar -xzf /tmp/$ArchiveName -C $RemotePath
        rm /tmp/$ArchiveName
        
        # Deploy
        cd $RemotePath
        docker compose down || true
        docker compose up -d --build
    "

    Write-Host "4. Cleaning up local archive..."
    Remove-Item $ArchiveName

    Write-Host "Deployment Complete! Visit http://${ServerIP}"
    ```

    **Copy and paste the above block into your PowerShell terminal.**

## Troubleshooting

- **Connection Refused**: Ensure the server allows SSH connections on port 22.
- **Permission Denied**: Verify the password is correct.
- **Docker Error**: The script attempts to install Docker automatically. If it fails, you may need to install Docker manually on the server.
