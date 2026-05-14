import csv
import time
import re
import random
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ————— Configuration —————
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/inven/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("--profile-directory=Default")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)
chrome_options.add_argument("--headless")


output_path = "C:/Users/inven/OneDrive/Documents/drawer-tracker-app/WeedmapsScraper/BuzzCANNABIS_Generalized.csv"
base_url = "https://buzzcannabis.com/menu/"

# Updated synonyms dict
raw_synonyms = {
    "flower": "Flower", "cart": "Cartridge", "cartridge": "Cartridge", "vape": "Cartridge", "Pod": "Cartridge",
    "vape cart": "Cartridge", "vape cartridge": "Cartridge", "aio": "All-in-one", "all-in-one": "All-in-one",
    "bev": "Beverage", "drink": "Beverage", "shot": "Beverage", "Tab": "Pill", "Tabs": "Pill", "Protab": "Pill",
    "preroll": "Preroll", "pre-roll": "Preroll", "joint": "Preroll", "infused preroll": "Preroll", "Blunt": "Preroll",
    "sugar": "Extract", "concentrate": "Extract", "wax": "Extract", "shatter": "Extract", "Blunts": "Preroll",
    "badder": "Extract", "live resin": "Extract", "rosin": "Extract", "hash": "Extract",
    "diamonds": "Extract", "crumble": "Extract", "sauce": "Extract", "LR": "Extract", "Split Jar": "Extract",
    "pill": "Pill", "capsule": "Pill", "tablet": "Pill", "RSO": "Extract", "RCT": "Edible",
    "edible": "Edible", "gummy": "Edible", "gummies": "Edible", "chocolate": "Edible", "choc": "Edible",
    "chew": "Edible", "candy": "Edible", "mint": "Edible", "cookie": "Edible", "brownie": "Edible",
    "nano belts": "Edible", "merch": "Merch", "merchandise": "Merch", "gear": "Merch", "apparel": "Merch",
    "tincture": "Tincture", "Bath Bomb": "Topical", "Patch": "Topical", "Muscle Freeze": "Topical",  "Body Oil": "Topical",
    "drops": "Tincture",  "Balm": "Topical", "sublingual": "Tincture", "battery": "Battery", "Syringe": "Extract",
}
# Normalize keys to lowercase for case-insensitive matching
synonyms = {k.lower(): v for k, v in raw_synonyms.items()}

# Updated special terms list (lowercased)
special_terms_list = [
    "pre-pack", "pod", "juice", "hash", "all-in-one", "tablet", "gummy", "510 thread", "pipe",
    "live resin", "lighter", "shot", "diamonds", "tea", "soda", "dropper", "live rosin", "accessory",
    "battery", "other", "rolling papers", "coffee", "chocolate", "capsule", "tonic", "rso", "chew",
    "balm", "baked good", "butter", "patch", "spray", "syrup", "bong", "distillate", "fso", "mints",
    "lotion", "live resin sauce", "grinder", "badder", "vaporizer", "cookie", "oil", "FI",
    "full spectrum oil", "hash rosin", "dab rig", "ice water hash", "tier 1", "tier 2", "tier 3", "LRO", "PLRE"
    "t1", "t2", "t3", "curepen", "solventless", "mixed light", "indoor", "black bag", "green bag", "2 pack",
    "white bag", "infused", "grey bag", "10 pack", "6 pack", "5 pack", "4 pack", "10pk", "6pk", "5pk", "4pk", "RSO"
]
special_terms = [term.lower() for term in special_terms_list]

# Storage for deduplication: (brand, category, weight) -> set(prices)
seen = defaultdict(set)

# ————— Helper Functions —————
def extract_weight_and_clean_price(name: str, price: str) -> (str, str):
    weight = ""
    price_clean = price

    # Match formats like ".5g", "0.5g", "3.5g", "100mg", etc.
    pattern = r"(?:/|\s)?(\d*\.\d+|\d+)\s*(g|mg|ml)\b"
    
    # Try name first
    match = re.search(pattern, name.lower())
    if not match:
        # Then try price field
        match = re.search(pattern, price.lower())

    if match:
        num = match.group(1)
        unit = match.group(2)
        if num.startswith("."):
            num = "0" + num  # fix ".5g" → "0.5g"
        weight = f"{num}{unit}"

        # Clean the weight info from price
        weight_pattern = re.escape(match.group(0))  # full match like "/.5g" or " .5g"
        price_clean = re.sub(weight_pattern, "", price_clean, flags=re.IGNORECASE).strip()

    # Apply final price cleaning to remove any remaining "/weight"
    price_clean = clean_price(price_clean)

    return weight, price_clean

def clean_price(price: str) -> str:
    # Remove "/<weight>" suffix (including '/1g', '/2g', etc.)
    return re.sub(r"/\s*\d+\.?\d*\s*(g|mg|ml)\b", "", price, flags=re.IGNORECASE).strip()

def detect_special_terms(name: str) -> str:
    l = name.lower()
    found = {term.title() for term in special_terms if term in l}
    return ", ".join(sorted(found))

def detect_category(name: str) -> (str, str):
    l = name.lower()
    for key, cat in synonyms.items():
        if key in l:
            return cat, ""
    return "Unknown", name  # debug_name = full name when unknown

# ————— Start Scraping —————
driver.get(base_url)
# wait & click age-gate
try:
    btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.age-gate-submit-yes")
    ))
    btn.click()
    print("✅ Confirmed age gate")
except Exception:
    print("⚠️ Age gate not found or already passed")

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Brand", "Category", "Weight",
        "Special Terms", "Price", "Original Price", "Debug Name"
    ])

    for page in range(1, 95):
        print(f"🔍 Scraping page {page}")
        try:
            # random delay & scroll into view
            time.sleep(random.uniform(3.5, 4.5))
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.joint-link[href*='?product_page=']")
            ))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2.5, 3.5))

            names = driver.find_elements(By.CSS_SELECTOR, "a.joint-link[href*='?product_page=']")
            brands = driver.find_elements(By.CSS_SELECTOR, "a.joint-link[href*='?brand_page=']")
            prices = driver.find_elements(By.CSS_SELECTOR, "div.joint-product-card-price")
            origs = driver.find_elements(By.CSS_SELECTOR, "div.joint-product-original-price")

            count = min(len(names), len(brands), len(prices))
            # Decide where to start skipping featured
            start_idx = 0 if page == 1 else 5

            for i in range(start_idx, count):
                name = names[i].text.strip()
                brand = brands[i].text.strip()
                raw_price = prices[i].text.strip()
                og_price = origs[i].text.strip() if i < len(origs) else ""

                # Updated weight and price extraction
                weight, price_clean = extract_weight_and_clean_price(name, raw_price)
                
                special_column = detect_special_terms(name)
                category, debug_name = detect_category(name)

                key = (brand, category, weight)
                if price_clean not in seen[key]:
                    seen[key].add(price_clean)
                    writer.writerow([
                        brand, category, weight,
                        special_column, price_clean, og_price, debug_name
                    ])


            print(f"✅ Page {page} done, wrote {count - start_idx} items")

            if page == 94:
                break

            # click next
            next_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//div[@aria-label='Go to page {page + 1}']")
            ))
            ActionChains(driver).move_to_element(next_btn).click(next_btn).perform()
            time.sleep(random.uniform(5.5, 6.5))

        except Exception as e:
            print(f"⚠️ Failed on page {page}: {e}")
            break

driver.quit()
print("🎉 Finished scraping Buzz Cannabis!")