import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import csv

# Set path to Tesseract executable (adjust if necessary)
# Use the correct attribute name so pytesseract can find the binary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define paths
UNKNOWN_FOLDER = r"C:\Users\inven\OneDrive\Documents\Invoices\Mass Invoices"
DISTRIBUTOR_LIST_CSV = r"C:\Users\inven\OneDrive\Documents\Automation\DistributorList.csv"

# CONFIGURABLE LIST OF COMMON DISTRIBUTOR NAMES THAT OFTEN FAIL DETECTION
# Add more names here as needed - they will be searched anywhere on the page
COMMON_FAILURE_DISTROS = [
    "GARDEN OF WEEDEN, INC",
    "GROWPACKER",
    "ELEVATION WELLNESS CENTER, INC.",
    "SD REALTY VENTURES II, LLC",
    "GP OPERATIONS, INC.",
    "HERITAGE HOLDINGS OF CALIFORNIA, INC.",
    "APOLLO CULTIVATION MANAGEMENT, LLC",
    "DASH INDUSTRIES",
    "FOUR STAR DISTRIBUTION AND DELIVERY LLC",
    "P&B LABS HUMBOLDT LLC",
    "MARY'S TECH",
    "HYPEEREON CORP",
    "GREEN ROCKET DESIGN",
    "BACK HOUSE",
    "FOUR STAR",
    "CROWN GENETICS",
    "CALIFORNIA ORGANIC",
    "SAINTS PLACE",
    "RUKLI",
    "PURE VAPE",
    "BROADWAY ALLIANCE",
    "EH TECH",
    "BEACH ENLIGHTENMENT",
    "FOO FLOWER",
    "DHS DEVELOPMENT",
    "BTC VENTURES",
    "THE REEFINERY",
    "YERBA BUENA",
    "SD STRAINS",
    "WCC MGMT",
    "GARDEN OF WEEDEN",
    "APOLLO CULTIVATION",
    "TIKUN OLAM",
    "MODERN LEAF",
    "SENSI FLORA",
    "CURE PRODUCTIONS",
    "ALKHEMIST",
    "SATELLITES DIP",
    "ZASP",
    "HDO13 HOLDINGS",
    "SD REALTY",
    "GF Distribution",
    "MICRO BUDDERY",
    "VEDA DIST",
    "CRAFTED CANOPY",
    "URBAN THERAPIES",
    "Elevation Wellness",
    "UPNORTH",
    "KDM",
    "SLO DRIVER",
    "THIRTYONE",
    "TERPX",
    "SSAL HORTICULTURE",
    "SACRAMENTO CONFIDENTIAL",
    "TOP HAT",
    "CI Distribution",
    "Kind House",
    "Wonderland",
    "RJRC",
    "GC GLOBAL",
    "HIGHSTAR",
    "OZ DISTRIBUTION",
    "DISCOUNT CARE",
    "CLAYBOURNE",
    "RMG",
    "CANNACO",
    "MELROSE",
    "BREEZ",
    "Humboldt Brand",
    "INDUS",
    "MOXIE",
    "PURE CA",
    "NABIS",
    "420-3",
    "CYPRESS",
    "ACCENTIAN",
    "GF DISTRIBUTION",
    "Lowell",
    "LMG Logistics",
]

def preprocess_image(img):
    """Enhance image quality for better OCR accuracy."""
    img = img.convert("L")  # Convert to grayscale
    img = img.filter(ImageFilter.MedianFilter(size=3))  # Reduce noise
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Increase contrast
    img = img.point(lambda p: 0 if p < 150 else 255)  # Apply binary thresholding
    return img

def extract_text_from_pdf(pdf_path):
    """Extracts all text from all pages of a PDF."""
    full_text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                print(f"📄 Processing page {page_num}...")
                
                text = page.get_text("text").strip()
                
                if not text:  # If no text is found, fallback to OCR
                    print(f"📄 Page {page_num}: No text found, attempting OCR...")
                    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # High DPI for OCR
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img = preprocess_image(img)
                    text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 6')
                
                full_text += text + "\n"
        
        return full_text
    except Exception as e:
        print(f"⚠️ Error extracting text from {pdf_path}: {e}")
        return ""

def find_distributor_name(text):
    """
    Searches through the entire text for any mention of the common failure distributors.
    If no match is found, falls back to searching for distributors in the CSV file.
    Returns the first match found, or None if no match is found.
    """
    text_upper = text.upper()
    
    # First, try to find a match in common failure distros
    for distro in COMMON_FAILURE_DISTROS:
        distro_upper = distro.upper()
        if distro_upper in text_upper:
            print(f"✅ Found distributor in common list: {distro}")
            return distro
    
    print("❌ No matching distributor found in common failure list.")
    
    # Fallback: Search in the CSV distributor list
    print(f"🔍 Searching in distributor CSV file: {DISTRIBUTOR_LIST_CSV}")
    return search_distributor_csv(text)

def search_distributor_csv(text):
    """
    Searches the CSV file (column A) for any mention of distributors in the text.
    Returns the first distributor found, or None if no match.
    """
    if not os.path.exists(DISTRIBUTOR_LIST_CSV):
        print(f"⚠️ CSV file not found: {DISTRIBUTOR_LIST_CSV}")
        return None
    
    text_upper = text.upper()
    
    try:
        with open(DISTRIBUTOR_LIST_CSV, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # Check if row is not empty
                    distributor = row[0].strip()  # Column A (first column)
                    if distributor and distributor.upper() in text_upper:
                        print(f"✅ Found distributor in CSV: {distributor}")
                        return distributor
        
        print("❌ No matching distributor found in CSV file either.")
        return None
    except Exception as e:
        print(f"⚠️ Error reading CSV file: {e}")
        return None

def clean_filename(name):
    """Removes spaces, commas, and special characters from a name."""
    return re.sub(r"\s+|[^a-zA-Z0-9]", "", name)

def process_unknown_files():
    """
    Scans the folder for files starting with 'unknown_' and attempts to identify
    the distributor name. Renames files with the matched distributor or leaves
    them as 'unknown' if no match is found.
    """
    unknown_count = 0
    processed_count = 0
    
    # List all files in the folder
    for file in os.listdir(UNKNOWN_FOLDER):
        if file.startswith("unknown_") and file.endswith(".pdf"):
            unknown_count += 1
            pdf_path = os.path.join(UNKNOWN_FOLDER, file)
            
            print(f"\n{'='*80}")
            print(f"Processing: {file}")
            print(f"{'='*80}")
            
            # Extract text from the PDF
            text = extract_text_from_pdf(pdf_path)
            
            # Try to find a matching distributor
            distributor_name = find_distributor_name(text)
            
            if distributor_name:
                # Extract the metrc number from the current filename if it exists
                # Format is typically: unknown_METRC#.pdf
                match = re.search(r"unknown_(.+)\.pdf", file)
                metrc_part = match.group(1) if match else "unknown"
                
                # Create new filename with the distributor name
                distributor_clean = clean_filename(distributor_name)
                new_filename = f"{distributor_clean}_{metrc_part}.pdf"
            else:
                # Leave it as unknown since no match was found
                new_filename = file
            
            # Rename the file
            if new_filename != file:
                new_path = os.path.join(UNKNOWN_FOLDER, new_filename)
                try:
                    os.rename(pdf_path, new_path)
                    print(f"✅ Renamed: {file} -> {new_filename}")
                    processed_count += 1
                except Exception as e:
                    print(f"⚠️ Error renaming {file}: {e}")
            else:
                print(f"⚠️ No changes made - distributor not found, keeping as: {file}")
    
    print(f"\n{'='*80}")
    print(f"Summary: Found {unknown_count} unknown files, processed {processed_count}")
    print(f"{'='*80}")

def add_custom_distributor(name):
    """
    Helper function to add a custom distributor to the list.
    Usage: add_custom_distributor("NEW DISTRIBUTOR NAME")
    """
    if name not in COMMON_FAILURE_DISTROS:
        COMMON_FAILURE_DISTROS.append(name)
        print(f"✅ Added '{name}' to the distributor list.")
    else:
        print(f"⚠️ '{name}' is already in the distributor list.")

if __name__ == "__main__":
    try:
        print("Starting Unknown Invoice Resolver...")
        process_unknown_files()
    except Exception as e:
        print(f"⚠️ Fatal error: {e}")
    input("Press Enter to exit.")

# USAGE NOTES:
# 1. Run this script to process all 'unknown_*.pdf' files in the Mass Invoices folder
# 2. To add more distributor names to check for, add them to COMMON_FAILURE_DISTROS list above
# 3. The script searches for exact matches (case-insensitive) anywhere on the page
# 4. Files are renamed with the matched distributor name, or left as 'unknown' if no match
#cd "C:\Users\inven\Documents\automation_and_documentation\invoice_metrc_extractor"
# (if needed for this session)
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
#.\venv\Scripts\Activate.ps1
#python metrc_unknown_resolver.py
# or, without activating:
#& ".\venv\Scripts\python.exe" metrc_unknown_resolver.py