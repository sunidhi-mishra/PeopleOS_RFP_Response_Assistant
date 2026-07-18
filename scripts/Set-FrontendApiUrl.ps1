param(
    [Parameter(Mandatory = $true)]
    [string]$ApiUrl
)

$frontendDir = Join-Path $PSScriptRoot '..\frontend'
$configPath = Join-Path $frontendDir 'config.js'

$configContent = @"
window.RFP_MATCH_CONFIG = {
    API_URL: "$ApiUrl"
};
"@

Set-Content -Path $configPath -Value $configContent -NoNewline
