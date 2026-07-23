<#
.SYNOPSIS
    Switches the frontend config.js between development and production environments.

.DESCRIPTION
    Copies config.dev.js or config.prod.js over config.js, or sets a custom API URL directly.

.PARAMETER Env
    Target environment: "dev" or "prod". Copies the matching config.*.js file.

.PARAMETER ApiUrl
    Set a custom API URL directly (overrides -Env). Useful for staging deployments.

.EXAMPLE
    # Switch to local development backend
    .\Set-FrontendApiUrl.ps1 -Env dev

.EXAMPLE
    # Switch to production backend
    .\Set-FrontendApiUrl.ps1 -Env prod

.EXAMPLE
    # Point to a custom staging URL
    .\Set-FrontendApiUrl.ps1 -ApiUrl "https://staging-backend.onrender.com/match"
#>

param(
    [Parameter(ParameterSetName = "ByEnv")]
    [ValidateSet("dev", "prod")]
    [string]$Env,

    [Parameter(ParameterSetName = "ByUrl", Mandatory = $true)]
    [string]$ApiUrl
)

$frontendDir = Join-Path $PSScriptRoot '..\frontend'
$configPath  = Join-Path $frontendDir 'config.js'

if ($PSCmdlet.ParameterSetName -eq "ByEnv") {
    $sourceFile = Join-Path $frontendDir "config.$Env.js"
    if (-not (Test-Path $sourceFile)) {
        Write-Error "Source file not found: $sourceFile"
        exit 1
    }
    Copy-Item -Path $sourceFile -Destination $configPath -Force
    Write-Host "[OK] config.js set to $Env environment (copied from config.$Env.js)"
} else {
    # Derive ENV label from URL
    $envLabel = if ($ApiUrl -match "127\.0\.0\.1|localhost") { "development" } else { "production" }

    $configContent = @"
// Active config — set by Set-FrontendApiUrl.ps1
window.RFP_MATCH_CONFIG = {
    API_URL: "$ApiUrl",
    ENV: "$envLabel"
};
"@
    Set-Content -Path $configPath -Value $configContent -NoNewline
    Write-Host "[OK] config.js set to custom URL: $ApiUrl (env=$envLabel)"
}
