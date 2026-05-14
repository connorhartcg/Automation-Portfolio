# Get the script directory
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path

# Go up two levels to reach the shared root folder
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDirectory)

# Define the full paths based on known structure
$csvPath = Join-Path $scriptDirectory "data_entry_sheet.csv"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$photoBasePath = Join-Path -Path $scriptDir -ChildPath "..\assets\brand_photos\Photos"
$photoBasePath = Resolve-Path -Path $photoBasePath

# Import CSV, assuming headers exist
$data = Import-Csv -Path $csvPath

# Initialize an array to store missing file paths
$missingFiles = @()

# Loop through each row
foreach ($row in $data) {
    $brand = $row.'Brand'
    $fileName = $row.'File Name'

    if (-not $brand -or -not $fileName) {
        continue
    }

    $brand = $brand.Trim().ToUpper()
    $fileName = $fileName.Trim().ToUpper()

    $filePathJpg = Join-Path -Path $photoBasePath -ChildPath "$brand\$fileName.jpg"
    $filePathPng = Join-Path -Path $photoBasePath -ChildPath "$brand\$fileName.png"

    if (-not (Test-Path -Path $filePathJpg -PathType Leaf) -and -not (Test-Path -Path $filePathPng -PathType Leaf)) {
        $missingFiles += "$brand\$fileName.(jpg/png) NOT FOUND"
    }
}

# Output result
if ($missingFiles.Count -gt 0) {
    Write-Output "Missing files:"
    $missingFiles | ForEach-Object { Write-Output $_ }
} else {
    Write-Output "All files exist."
}
Read-Host "Press Enter to exit"


