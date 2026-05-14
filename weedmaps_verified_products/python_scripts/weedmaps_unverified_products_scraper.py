import csv
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def initialize_driver():
    """Initialize the Selenium WebDriver with the correct options."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    # Use the default Chrome profile (adjust the path to your profile)
    profile_path = r"C:\Users\inven\AppData\Local\Google\Chrome\User Data"  # Modify if necessary
    chrome_options.add_argument(f"user-data-dir={profile_path}")  # Path to your user data
    chrome_options.add_argument("profile-directory=Default")  # Replace 'Default' with the actual profile name if necessary

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def scrape_brand_products(driver, brand, start_url):
    """Scrape products for a specific brand from the given URL."""
    product_names = []
    page_number = 1

    print(f"🔍 Scraping brand: {brand}")
    while True:
        url = start_url if page_number == 1 else f"{start_url}?page={page_number}"
        print(f"🌐 Visiting: {url}")
        driver.get(url)

        # Wait for CAPTCHA clearance + natural delay
        if page_number == 1:
            print("⏳ Waiting 15 seconds on first page...")
            time.sleep(15)
        else:
            delay = random.uniform(2, 5)
            print(f"⏳ Waiting {delay:.2f} seconds before scraping...")
            time.sleep(delay)

        # Try to grab all product title elements
        try:
            items = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-card-title"]')
            scraped = [el.text.strip() for el in items if el.text.strip()]
            print(f"✅ Found {len(scraped)} products on page {page_number}")

            product_names.extend(scraped)

            # Stop if less than 50 products
            if len(scraped) < 50:
                print("🔚 Reached last page for brand.")
                break

            # Wait before next page
            time.sleep(random.uniform(2, 5))
            page_number += 1
        except Exception as e:
            print("⚠️ Scrape error:", e)
            break

    # Append results to CSV
    if product_names:
        write_header = not os.path.exists(OUTPUT_PATH)
        with open(OUTPUT_PATH, mode="a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["Product Name", "Brand"])
            for name in product_names:
                writer.writerow([name, brand])
        print(f"💾 Saved {len(product_names)} products for {brand}")
    else:
        print(f"❌ No products found for {brand}")

def main():
    # ==== File paths ====
    UNVERIFIED_PATH = r"C:\Users\inven\OneDrive\Documents\drawer-tracker-app\WeedmapsScraper\UnverifiedProducts - Brands.csv"
    OUTPUT_PATH = r"C:\Users\inven\OneDrive\Documents\drawer-tracker-app\WeedmapsScraper\CAM_Products.csv"

    # ==== Load unverified brand list ====
    with open(UNVERIFIED_PATH, newline='', encoding='utf-8') as f:
        unverified_brands = [row[0].strip() for row in csv.reader(f) if row]

    # ==== Load already-scraped brands from output ====
    verified_brands = set()
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) > 1:
                    verified_brands.add(row[1].strip().lower())

    # ==== Filter only new brands to scrape ====
    brands_to_scrape = [b for b in unverified_brands if b.lower() not in verified_brands]

    # ==== Initialize WebDriver ====
    driver = initialize_driver()

    # ==== Run scrape for all new brands ====
    for brand in brands_to_scrape:
        slug = brand.lower().replace(" ", "-")
        brand_url = f"https://weedmaps.com/brands/{slug}/products"
        scrape_brand_products(driver, brand, brand_url)

    # ==== Clean up ====
    driver.quit()
    print("🎉 All done!")

if __name__ == "__main__":
    main()
