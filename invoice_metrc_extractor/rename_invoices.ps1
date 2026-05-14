$folderPath = "C:\Users\inven\OneDrive\Documents\Invoices\Mass Invoices"

# Get all PDF files in the specified folder
$pdfFiles = Get-ChildItem -Path $folderPath -Filter "*.pdf"

# Initialize counter
$count = 1

# Loop through each PDF file and rename
foreach ($file in $pdfFiles) {
    # Define the new name
    $newName = "kyoScan_$count.pdf"
    
    # Get the full path of the new file name
    $newPath = Join-Path -Path $folderPath -ChildPath $newName
    
    # Rename the file
    Rename-Item -Path $file.FullName -NewName $newPath
    
    # Increment the counter
    $count++
}

Write-Host "Renaming complete!"