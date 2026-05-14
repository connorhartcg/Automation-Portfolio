# Define paths
$downloadFolder = [Environment]::GetFolderPath('UserProfile') + "\Downloads"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Filenames
$fileNameToDetect = "DataEntrySheet - Export Sheet.csv"
$expectedName = "data_entry_sheet.csv"

Write-Host "📁 Monitoring for '$fileNameToDetect' every 5 seconds..."
Write-Host "📥 From: $downloadFolder"
Write-Host "📂 To:   $scriptDir`n"

while ($true) {
    $sourceFile = Join-Path $downloadFolder $fileNameToDetect
    $targetFile = Join-Path $scriptDir $expectedName

    if (Test-Path $sourceFile) {
        Write-Host "✅ Found: $sourceFile"

        # Delete existing file in target folder
        if (Test-Path $targetFile) {
            Remove-Item $targetFile -Force
            Write-Host "🗑️ Deleted existing: $targetFile"
        }

        # Move and rename
        Move-Item $sourceFile $targetFile
        Write-Host "📦 Moved to: $targetFile`n"
    }

    Start-Sleep -Seconds 5
}
