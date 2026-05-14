from playwright.sync_api import sync_playwright
import csv
import re
import time
import random
from collections import defaultdict

# Configuration
output_path = r"C:/Users/inven/Documents/drawer-tracker-app/WeedmapsScraper/BuzzCANNABIS_Generalized_playwright.csv"
base_url = "https://buzzcannabis.com/menu/"

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

synonyms = {k.lower(): v for k, v in raw_synonyms.items()}

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

seen = defaultdict(set)


def extract_weight_and_clean_price(name: str, price: str):
    weight = ""
    price_clean = price
    pattern = r"(?:/|\s)?(\d*\.\d+|\d+)\s*(g|mg|ml)\b"
    match = re.search(pattern, name.lower())
    if not match:
        match = re.search(pattern, price.lower())
    if match:
        num = match.group(1)
        unit = match.group(2)
        if num.startswith('.'):
            num = '0' + num
        weight = f"{num}{unit}"
        weight_pattern = re.escape(match.group(0))
        price_clean = re.sub(weight_pattern, "", price_clean, flags=re.IGNORECASE).strip()
    price_clean = clean_price(price_clean)
    return weight, price_clean


def clean_price(price: str) -> str:
    return re.sub(r"/\s*\d+\.?\d*\s*(g|mg|ml)\b", "", price, flags=re.IGNORECASE).strip()


def detect_special_terms(name: str) -> str:
    l = name.lower()
    found = {term.title() for term in special_terms if term in l}
    return ", ".join(sorted(found))


def detect_category(name: str):
    l = name.lower()
    for key, cat in synonyms.items():
        if key in l:
            return cat, ""
    return "Unknown", name


with sync_playwright() as p:
    # Launch visible browser for debugging. Remove headless=False when done.
    browser = p.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context()
    page = context.new_page()

    page.goto(base_url, timeout=60000)

    # handle age gate
    try:
        page.click("button.age-gate-submit-yes", timeout=5000)
        print("✅ Confirmed age gate")
    except Exception:
        print("⚠️ Age gate not found or already passed")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Brand", "Category", "Weight",
            "Special Terms", "Price", "Original Price", "Debug Name"
        ])

        for page_num in range(1, 95):
            print(f"🔍 Scraping page {page_num}")
            try:
                # random delay & scroll
                time.sleep(random.uniform(2.0, 4.0))
                page.wait_for_selector("a.joint-link[href*='?product_page=']", timeout=30000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.5, 2.5))

                names = page.query_selector_all("a.joint-link[href*='?product_page=']")
                # brand links use ?brand_name= in the href now per user-provided sample
                brands = page.query_selector_all("a.joint-link[href*='?brand_name=']")
                prices = page.query_selector_all("div.joint-product-card-price")
                origs = page.query_selector_all("div.joint-product-original-price")

                count = min(len(names), len(brands), len(prices))
                # debug: print counts and first few items to inspect selectors
                print(f"  found names={len(names)} brands={len(brands)} prices={len(prices)} origs={len(origs)} count={count}")
                if count > 0:
                    sample_n = min(3, count)
                    samples = []
                    for j in range(sample_n):
                        try:
                            samples.append((names[j].inner_text().strip(), brands[j].inner_text().strip(), prices[j].inner_text().strip()))
                        except Exception:
                            pass
                    print("  sample items:")
                    for s in samples:
                        print("   ", s)
                start_idx = 0 if page_num == 1 else 5

                for i in range(start_idx, count):
                    name = names[i].inner_text().strip()
                    brand = brands[i].inner_text().strip()
                    raw_price = prices[i].inner_text().strip()
                    og_price = origs[i].inner_text().strip() if i < len(origs) else ""

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

                print(f"✅ Page {page_num} done, wrote {count - start_idx} items")

                if page_num == 94:
                    break

                # click next button
                next_btn = page.wait_for_selector(f"div[aria-label='Go to page {page_num + 1}']", timeout=15000)
                next_btn.scroll_into_view_if_needed()
                next_btn.click()
                time.sleep(random.uniform(4.0, 6.0))

            except Exception as e:
                print(f"⚠️ Failed on page {page_num}: {e}")
                break

    context.close()
    browser.close()

print("🎉 Finished scraping Buzz Cannabis!")
