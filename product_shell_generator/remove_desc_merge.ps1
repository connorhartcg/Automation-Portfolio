# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Paths to CSV files
$dataEntrySheetPath = Join-Path $scriptDir "data_entry_sheet.csv"
$productListPath = Join-Path $scriptDir "product_list.csv"

# Load CSVs
try {
    $dataEntrySheet = Import-Csv -Path $dataEntrySheetPath -ErrorAction Stop
    $productList = Import-Csv -Path $productListPath -ErrorAction Stop
} catch {
    Write-Output "Error reading CSV files: $_"
    Read-Host -Prompt "Press Enter to exit"
    exit
}

# Validate product list
if (-not $productList -or $productList.Count -eq 0) {
    Write-Output "Product list is empty or unreadable."
    Read-Host -Prompt "Press Enter to exit"
    exit
}

# Extract names from product list
$productListNames = $productList | ForEach-Object { $_."Name".Trim() }

# Filter new products
$filteredData = $dataEntrySheet | Where-Object {
    $productName = $_."Product Name".Trim()
    $productListNames -notcontains $productName
}

if ($filteredData.Count -eq 0) {
    Write-Output "No new products to process."
    Read-Host -Prompt "Press Enter to exit"
    exit
}

foreach ($row in $filteredData) {
    $productName = $row."Product Name".Trim()

    # Skip unwanted terms
    if ($productName -match "DISPLAY|PROMO|ZAMPLE|SAMPLE") {
        Write-Output "Skipping: $productName (Excluded Keyword)"
        continue
    }

    Write-Output "Processing: $productName"

    # Generate description
    $body = @{
        model = "ProductGenerator"
        prompt = $productName
        stream = $false
    } | ConvertTo-Json -Depth 2

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
        $description = $response.response
    } catch {
        Write-Output "Failed to fetch description for: $productName. Error: $_"
        $description = "Error retrieving description"
    }

    $row."description" = $description
}

# Save updated CSV
try {
    $filteredData | Export-Csv -Path $dataEntrySheetPath -NoTypeInformation -Force
    Write-Output "Descriptions added and file updated successfully."
} catch {
    Write-Output "Failed to export updated CSV: $_"
}

Read-Host -Prompt "Press Enter to close the script"
