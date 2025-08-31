# JMS to Clash Converter - PowerShell Installation Script
# This script downloads and installs the latest release of jms2clash on Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("install", "uninstall")]
    [string]$Action = "install",

    [string]$InstallDir = "$env:LOCALAPPDATA\jms2clash",
    [switch]$Global,
    [switch]$Help
)

# Configuration
$Script:REPO = "skywardpixel/jms2clash"
$Script:BINARY_NAME = "jms2clash.exe"

# Use global install directory if -Global is specified
if ($Global) {
    $InstallDir = "$env:ProgramFiles\jms2clash"
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
    exit 1
}

function Show-Usage {
    Write-Host "JMS to Clash Converter - PowerShell Installation Script"
    Write-Host ""
    Write-Host "Usage: .\install.ps1 [ACTION] [OPTIONS]"
    Write-Host ""
    Write-Host "Actions:"
    Write-Host "  install      Install or update jms2clash (default)"
    Write-Host "  uninstall    Remove jms2clash"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -InstallDir  Set installation directory (default: %LOCALAPPDATA%\jms2clash)"
    Write-Host "  -Global      Install globally to Program Files (requires admin)"
    Write-Host "  -Help        Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1                        # Install locally"
    Write-Host "  .\install.ps1 -Global                # Install globally (requires admin)"
    Write-Host "  .\install.ps1 -InstallDir C:\tools   # Install to custom directory"
    Write-Host "  .\install.ps1 uninstall              # Remove jms2clash"
}

function Test-AdminRights {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-LatestRelease {
    Write-Info "Fetching latest release information..."

    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$Script:REPO/releases/latest" -UseBasicParsing
        return $response
    }
    catch {
        Write-Error "Failed to fetch release information: $_"
    }
}

function Add-ToPath {
    param([string]$Directory)

    # Check if directory is already in PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -split ";" -contains $Directory) {
        Write-Info "Directory already in PATH: $Directory"
        return
    }

    Write-Info "Adding to PATH: $Directory"

    try {
        $newPath = "$currentPath;$Directory"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

        # Also add to current session
        $env:PATH += ";$Directory"

        Write-Success "Added to PATH successfully"
    }
    catch {
        Write-Warning "Failed to add to PATH: $_"
        Write-Info "You may need to manually add $Directory to your PATH"
    }
}

function Remove-FromPath {
    param([string]$Directory)

    Write-Info "Removing from PATH: $Directory"

    try {
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        $pathArray = $currentPath -split ";" | Where-Object { $_ -ne $Directory }
        $newPath = $pathArray -join ";"

        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Success "Removed from PATH successfully"
    }
    catch {
        Write-Warning "Failed to remove from PATH: $_"
    }
}

function Install-Binary {
    # Check admin rights if installing globally
    if ($Global -and -not (Test-AdminRights)) {
        Write-Error "Global installation requires administrator rights. Run PowerShell as Administrator or remove -Global flag."
    }

    Write-Info "Installing jms2clash to: $InstallDir"

    # Get latest release
    $release = Get-LatestRelease
    $tagName = $release.tag_name

    if (-not $tagName) {
        Write-Error "Failed to get latest release information"
    }

    Write-Success "Found latest release: $tagName"

    # Download URL
    $downloadUrl = "https://github.com/$Script:REPO/releases/download/$tagName/jms2clash-windows-x64.zip"
    $tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_.FullName }
    $archiveFile = Join-Path $tempDir.FullName "jms2clash-windows-x64.zip"

    Write-Info "Downloading from: $downloadUrl"

    try {
        # Download with progress
        $ProgressPreference = 'Continue'
        Invoke-WebRequest -Uri $downloadUrl -OutFile $archiveFile -UseBasicParsing

        if (-not (Test-Path $archiveFile)) {
            Write-Error "Download failed"
        }

        Write-Success "Download completed"

        # Extract archive
        Write-Info "Extracting archive..."
        Expand-Archive -Path $archiveFile -DestinationPath $tempDir.FullName -Force

        # Find binary
        $binaryPath = Get-ChildItem -Path $tempDir.FullName -Name $Script:BINARY_NAME -Recurse -File | Select-Object -First 1

        if (-not $binaryPath) {
            Write-Error "Binary not found in archive"
        }

        $sourcePath = Join-Path $tempDir.FullName $binaryPath

        # Create install directory
        if (-not (Test-Path $InstallDir)) {
            Write-Info "Creating install directory: $InstallDir"
            New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        }

        # Install binary
        $installPath = Join-Path $InstallDir $Script:BINARY_NAME
        Write-Info "Installing binary to: $installPath"

        Copy-Item -Path $sourcePath -Destination $installPath -Force

        # Cleanup temp files
        Remove-Item -Path $tempDir.FullName -Recurse -Force

        Write-Success "Installation completed!"

        # Add to PATH if not global installation
        if (-not $Global) {
            Add-ToPath -Directory $InstallDir
        }

        # Verify installation
        try {
            $version = & $installPath --version 2>&1 | Select-Object -First 1
            Write-Success "Installed version: $version"
        }
        catch {
            Write-Warning "Binary installed but verification failed. You may need to restart your terminal."
        }
    }
    catch {
        Write-Error "Installation failed: $_"
    }
}

function Uninstall-Binary {
    $installPath = Join-Path $InstallDir $Script:BINARY_NAME

    if (Test-Path $installPath) {
        Write-Info "Removing $installPath"

        try {
            Remove-Item -Path $installPath -Force
            Write-Success "Binary removed successfully"

            # Remove from PATH if directory is empty
            if ((Get-ChildItem $InstallDir -ErrorAction SilentlyContinue).Count -eq 0) {
                Remove-FromPath -Directory $InstallDir
                Remove-Item -Path $InstallDir -Force -ErrorAction SilentlyContinue
            }
        }
        catch {
            Write-Error "Failed to remove binary: $_"
        }
    }
    else {
        Write-Warning "Binary not found at $installPath"
    }
}

# Main execution
if ($Help) {
    Show-Usage
    exit 0
}

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Error "PowerShell 5.0 or later is required"
}

# Execute action
switch ($Action) {
    "install" {
        Install-Binary
        Write-Host ""
        Write-Info "Quick start:"
        Write-Host "  curl -s `"https://your-subscription-url`" | jms2clash > config.yaml"
        Write-Host "  Get-Content subscription.txt | jms2clash > config.yaml"
        Write-Host ""
        Write-Info "For more information, visit: https://github.com/$Script:REPO"

        if (-not $Global) {
            Write-Host ""
            Write-Warning "You may need to restart your terminal for PATH changes to take effect."
        }
    }

    "uninstall" {
        Uninstall-Binary
    }

    default {
        Write-Error "Unknown action: $Action. Use -Help for usage information."
    }
}
