import os
import time
import shutil
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import csv
from difflib import get_close_matches

# Set path to Tesseract executable (adjust if necessary)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define paths
WATCH_FOLDER = r"C:\Users\inven\Downloads"
DEST_FOLDER = r"C:\Users\inven\OneDrive\Documents\Invoices\Mass Invoices"
DISTRIBUTOR_LIST_PATH = r"C:\Users\inven\OneDrive\Documents\Automation\DistributorList.csv"

# Ensure destination folder exists
os.makedirs(DEST_FOLDER, exist_ok=True)

# Load distributor names
def load_distributor_list():
    """Loads distributor names from CSV."""
    try:
        with open(DISTRIBUTOR_LIST_PATH, newline='', encoding='utf-8') as f:
            return [row[0].strip().upper() for row in csv.reader(f) if row]
    except Exception as e:
        print(f"⚠️ Error loading distributor list: {e}")
        return []

distributor_list = load_distributor_list()
print(f"✅ Loaded {len(distributor_list)} distributor names.")

def preprocess_image(img):
    """Enhance image quality for better OCR accuracy."""
    img = img.convert("L")  # Convert to grayscale
    img = img.filter(ImageFilter.MedianFilter(size=3))  # Reduce noise
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Increase contrast
    img = img.point(lambda p: 0 if p < 150 else 255)  # Apply binary thresholding
    return img

def extract_metrc_number(text):
    """Extracts the METRC number from text."""
    match = re.search(r"Manifest\s*No[\s\.\(\)\-\[]*\D*(\d{10})", text, re.IGNORECASE)
    if match:
        metrc_number = match.group(1)
        last_six_digits = metrc_number[-6:]
        print(f"✅ Found METRC Number: {metrc_number} -> Using last 6 digits: {last_six_digits}")
        return last_six_digits
    print("❌ METRC number not found.")
    return None

def extract_distributor_name(text):
    """Extracts distributor name and finds the closest match from the list."""
    # Try to directly match distributor names from the text
    for distributor in distributor_list:
        if distributor in text:
            print(f"✅ Found distributor name: {distributor}")
            return distributor

    # If no direct match, fall back to fuzzy matching
    extracted_name = re.sub(r"[^a-zA-Z0-9\s]", "", text).strip().upper()
    closest_match = get_close_matches(extracted_name, distributor_list, n=1, cutoff=0.7)
    best_match = closest_match[0] if closest_match else None

    if best_match:
        best_match_clean = re.sub(r"\s+|[^a-zA-Z0-9]", "", best_match)
        print(f"✅ Matched Distributor Name: {best_match_clean}")
        return best_match_clean
    else:
        print(f"❌ No close match found for: {extracted_name}")
    
    return None

def process_pdf(pdf_path):
    """Extracts METRC number and distributor name from a PDF."""
    try:
        with fitz.open(pdf_path) as doc:
            found_metrc = False
            found_distributor = False

            # Iterate over all pages in the document
            for page_num, page in enumerate(doc, start=1):
                print(f"📄 Processing page {page_num} of {pdf_path}...")

                text = page.get_text("text").strip()

                if not text:  # If no text is found, fallback to OCR
                    print(f"📄 Extracting via OCR for page {page_num} of {pdf_path}")
                    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # High DPI for OCR
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img = preprocess_image(img)
                    text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 6')

                # Log text extraction result
                print(f"📄 Extracted text from {pdf_path}, page {page_num}:\n{text}\n{'-'*80}")
                
                # Extract METRC number and distributor name only once (don't repeat work)
                if not found_metrc:
                    metrc_number = extract_metrc_number(text)
                    if metrc_number:
                        found_metrc = True

                if not found_distributor:
                    distributor_name = extract_distributor_name(text)
                    if distributor_name:
                        found_distributor = True

                # If both METRC and distributor are found, no need to continue processing further pages
                if found_metrc and found_distributor:
                    break  # Stop after finding both

    except Exception as e:
        print(f"⚠️ Error processing {pdf_path}: {e}")
    
    return distributor_name, metrc_number

def get_unique_filename(base_name, folder):
    """Generates a unique filename by appending a number if needed."""
    counter = 1
    new_name = base_name
    while os.path.exists(os.path.join(folder, new_name + ".pdf")):
        new_name = f"{base_name}_{counter}"
        counter += 1
    return new_name + ".pdf"

def rename_pdfs():
    """Scans and renames PDFs in the folder with '<DistributorName>_<METRC#>'."""
    for file in os.listdir(WATCH_FOLDER):
        if file.endswith(".pdf") and file.startswith("kyoScan"):
            pdf_path = os.path.join(WATCH_FOLDER, file)
            distributor_name, metrc_number = process_pdf(pdf_path)

            # Ensure we always use a METRC number if available
            final_distributor = distributor_name if distributor_name else "unknown"
            final_metrc = metrc_number if metrc_number else "unknown"

            # Clean up distributor name: remove spaces, commas, and special characters
            final_distributor_clean = re.sub(r"\s+|[^a-zA-Z0-9]", "", final_distributor)

            new_base_name = f"{final_distributor_clean}_{final_metrc}"
            new_name = get_unique_filename(new_base_name, WATCH_FOLDER)
            new_path = os.path.join(WATCH_FOLDER, new_name)
            
            try:
                os.rename(pdf_path, new_path)
                print(f"✅ Renamed: {file} -> {new_name}")

                # Move the renamed file to the destination folder
                dest_path = os.path.join(DEST_FOLDER, new_name)
                shutil.move(new_path, dest_path)
                print(f"✅ Moved: {new_name} -> {DEST_FOLDER}")
                
            except Exception as e:
                print(f"⚠️ Error renaming or moving {file}: {e}")

def move_files():
    """Monitors the source folder for new kyoScan files."""
    while True:
        rename_pdfs()
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    try:
        print("Monitoring folder for new kyoScan files...")
        move_files()
    except Exception as e:
        print(f"⚠️ Error occurred: {e}")
    input("Press Enter to exit.")

#python3 "C:\Users\inven\OneDrive\Documents\RenameScans.py"