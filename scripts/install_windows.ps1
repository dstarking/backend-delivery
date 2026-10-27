<#
Install backend-delivery for Codex, Claude Code, or both.
Run locally after extracting the ZIP, for example:
  powershell -ExecutionPolicy Bypass -File .\backend-delivery\scripts\install_windows.ps1 -Target Both -Scope User
Existing skill folders are never overwritten.
#>
param(
    [ValidateSet('Codex','Claude','Both')]
    [string]$Target = 'Both',
    [ValidateSet('User','Project')]
    [string]$Scope = 'User',
    [string]$Repo = ''
)
$ErrorActionPreference = 'Stop'
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not (Test-Path (Join-Path $skillRoot 'SKILL.md'))) {
    throw 'SKILL.md not found in parent directory.'
}
if ($Scope -eq 'Project') {
    if (-not $Repo -or -not (Test-Path -LiteralPath $Repo -PathType Container)) {
        throw 'When -Scope Project is used, pass an existing repository directory with -Repo.'
    }
    $base = (Resolve-Path -LiteralPath $Repo).Path
} else {
    $base = $env:USERPROFILE
}
$targets = @()
if ($Target -in @('Codex','Both')) { $targets += 'Codex' }
if ($Target -in @('Claude','Both')) { $targets += 'Claude' }
foreach ($name in $targets) {
    if ($name -eq 'Codex') {
        $parent = Join-Path $base '.agents\skills'
    } else {
        $parent = Join-Path $base '.claude\skills'
    }
    $dest = Join-Path $parent 'backend-delivery'
    if (Test-Path -LiteralPath $dest) {
        Write-Warning "SKIPPED: $dest already exists. No files were overwritten."
        continue
    }
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Copy-Item -LiteralPath $skillRoot -Destination $dest -Recurse
    Write-Host "INSTALLED: $dest"
}
Write-Host 'Start a new Codex or Claude Code session if the skill is not visible.'
