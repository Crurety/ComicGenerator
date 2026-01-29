$ServerIP = "122.51.215.20"
$User = "root"
$PubKeyPath = "d:\Project\PycharmProjects\ComicGenerator\id_ed25519.pub"

if (-not (Test-Path $PubKeyPath)) {
    Write-Error "Public key file not found at $PubKeyPath"
    exit 1
}

$PubKey = Get-Content -Path $PubKeyPath -Raw
$PubKey = $PubKey.Trim()

Write-Host "============================================="
Write-Host "  Uploading SSH Public Key to $ServerIP"
Write-Host "============================================="
Write-Host "You will be asked for the server password ($User)."
Write-Host ""

$RemoteCommand = "mkdir -p ~/.ssh; echo '$PubKey' >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys"

ssh $User@$ServerIP $RemoteCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Success! Public key configured on server."
    Write-Host "You can now test connectivity with: ssh -i d:\Project\PycharmProjects\ComicGenerator\id_ed25519 $User@$ServerIP"
} else {
    Write-Host ""
    Write-Host "❌ Failed to configure key. Please check your password and try again."
}
