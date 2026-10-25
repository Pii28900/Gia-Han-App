param([string]$Target = 'dist/SoGiaHan.exe')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$report = [ordered]@{
    outcome = 'NotVerified'
    reviewCommit = $env:GITHUB_SHA
    sourceRunId = $(if ($env:SOURCE_RUN_ID) { $env:SOURCE_RUN_ID } else { $env:GITHUB_RUN_ID })
    scannedAtUtc = [DateTime]::UtcNow.ToString('o')
    file = $Target
    sha256 = $null
    signatureStatus = $null
    engineVersion = $null
    signatureVersion = $null
    signatureUpdatedAt = $null
    scannerExitCode = $null
    message = 'Verification has not completed.'
}
New-Item -ItemType Directory -Path 'security-report' -Force | Out-Null
try {
    $full = (Resolve-Path -LiteralPath $Target).Path
    $report.sha256 = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
    $report.signatureStatus = [string](Get-AuthenticodeSignature -LiteralPath $full).Status
    $platform = Join-Path $env:ProgramData 'Microsoft\Windows Defender\Platform'
    $candidates = @()
    if (Test-Path -LiteralPath $platform) {
        $candidates += Get-ChildItem -LiteralPath $platform -Directory |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'MpCmdRun.exe' }
    }
    $candidates += Join-Path $env:ProgramFiles 'Windows Defender\MpCmdRun.exe'
    $scanner = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $scanner) { throw 'Microsoft Defender scanner is unavailable on this runner.' }
    & $scanner -SignatureUpdate
    if ($LASTEXITCODE -ne 0) { throw "Defender signature update failed: $LASTEXITCODE" }
    $status = Get-MpComputerStatus -ErrorAction Stop
    if (-not $status.AntivirusSignatureVersion) { throw 'Cannot verify the Defender signature database.' }
    $report.engineVersion = [string]$status.AMEngineVersion
    $report.signatureVersion = [string]$status.AntivirusSignatureVersion
    $report.signatureUpdatedAt = $status.AntivirusSignatureLastUpdated.ToUniversalTime().ToString('o')
    & $scanner -Scan -ScanType 3 -File $full
    $report.scannerExitCode = $LASTEXITCODE
    if ($LASTEXITCODE -ne 0) { throw "Defender scan did not pass: $LASTEXITCODE" }
    if (-not (Test-Path -LiteralPath $full)) { throw 'The executable was removed or quarantined during scanning.' }
    $detections = @(Get-MpThreatDetection -ErrorAction Stop | Where-Object {
        @($_.Resources | Where-Object { $_ -like "*$full*" }).Count -gt 0
    })
    if ($detections.Count -gt 0) { throw 'Defender recorded a detection for this executable. Do not distribute it.' }
    $after = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($after -ne $report.sha256) { throw 'Executable changed during verification.' }
    $report.outcome = 'NoThreatsDetected'
    $report.message = 'Microsoft Defender reported no threats for this SHA-256 at the recorded scan time. This does not establish a Google Safe Browsing verdict.'
    "$($report.sha256)  SoGiaHan.exe" | Set-Content -LiteralPath 'dist/SoGiaHan.exe.sha256' -Encoding ascii
} catch {
    $report.outcome = 'BlockedOrUnverified'
    $report.message = $_.Exception.Message
    throw
} finally {
    $json = $report | ConvertTo-Json -Depth 4
    $json | Set-Content -LiteralPath 'security-report/defender-report.json' -Encoding utf8
    $summary = "## Windows executable security verification`n`n``````json`n$json`n```````n"
    $summary | Set-Content -LiteralPath 'security-report/summary.md' -Encoding utf8
    if ($env:GITHUB_STEP_SUMMARY) { $summary | Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY -Encoding utf8 }
}
