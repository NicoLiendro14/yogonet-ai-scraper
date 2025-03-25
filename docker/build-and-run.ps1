$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectDir = Split-Path -Parent $ScriptDir

$ImageName = "yogonet-scraper"
$Tag = "latest"
$CredentialsPath = Join-Path -Path $ProjectDir -ChildPath "creds.json"
$OutputDir = Join-Path -Path $ProjectDir -ChildPath "output"

Write-Host "===== Yogonet News Scraper Docker Build & Run =====" -ForegroundColor Cyan
Write-Host "Project directory: $ProjectDir"
Write-Host "Credentials path: $CredentialsPath"
Write-Host "Output directory: $OutputDir"

if (-not (Test-Path $CredentialsPath)) {
    Write-Host "Error: Google Cloud credentials file not found at $CredentialsPath" -ForegroundColor Red
    Write-Host "Please place your credentials file at the specified location or update the script." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory | Out-Null
}

$CredentialsContent = Get-Content -Raw -Path $CredentialsPath | ConvertFrom-Json
$ProjectId = $CredentialsContent.project_id

if (-not $ProjectId) {
    Write-Host "Error: Could not extract project_id from credentials file." -ForegroundColor Red
    exit 1
}

Write-Host "`n===== Building Docker Image =====" -ForegroundColor Cyan
$DockerfilePath = Join-Path -Path $ScriptDir -ChildPath "Dockerfile"
docker build -t "${ImageName}:${Tag}" -f $DockerfilePath $ProjectDir

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n===== Docker Image Built Successfully =====" -ForegroundColor Green
Write-Host "Image: ${ImageName}:${Tag}"

Write-Host "`n===== Running Docker Container =====" -ForegroundColor Cyan

$OutputDirDocker = $OutputDir -replace "\\", "/" -replace "C:", "/c"
$CredentialsDirDocker = $CredentialsPath -replace "\\", "/" -replace "C:", "/c"

docker run -it --rm `
    -v "${OutputDirDocker}:/app/output" `
    -v "${CredentialsDirDocker}:/app/credentials/service_account.json" `
    -e GOOGLE_CLOUD_PROJECT="$ProjectId" `
    "${ImageName}:${Tag}"

Write-Host "`n===== Container Execution Complete =====" -ForegroundColor Green
Write-Host "Check the output directory for results: $OutputDir" 