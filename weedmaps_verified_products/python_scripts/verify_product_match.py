import pandas as pd
from difflib import SequenceMatcher
import os
import re

# Load data
input_path = r"C:\Users\inven\OneDrive\Documents\drawer-tracker-app\WeedmapsScraper\UnverifiedComparison.csv"
output_path = os.path.join(os.path.dirname(input_path), "UnverifiedComparison_Matched.csv")
df = pd.read_csv(input_path)
df.columns = ['Verified Product', 'Verified Brand', 'Category', 'My Brand', 'My Product']

# Synonyms for normalization
synonyms = {
    'gummy': 'gummies',
    'pod': 'cartridge',
    'aio': 'all-in-one',
    'vape': 'cartridge',
    'cart': 'cartridge',
    'liiil': 'all-in-one',
    '4 pack': '4pk', '5 pack': '5pk',
    '0.5g': '.5g', '3.5 g': '3.5g', '1 g': '1g', '7 g': '7g', '14 g': '14g', '28 g': '28g',
    'one ounce': '28g', 'ounce': '28g', 'oz': '28g', '1oz': '28g'
}

def normalize(text):
    if pd.isna(text):
        return ''
    text = str(text).lower()
    for src, target in synonyms.items():
        text = text.replace(src, target)
    return re.sub(r'[^a-z0-9\s]', '', text).strip()

def parse_weight_and_pack(text):
    text = text.lower()
    weight_match = re.findall(r'(\d+(?:\.\d+)?)(g|mg|oz)', text)
    pack_match = re.search(r'(\d+)\s?(?:pack|pk)', text)

    if not weight_match:
        return '', 1  # Default to 1 pack if weight is present but pack isn't

    weight_val, unit = weight_match[0]
    weight_val = float(weight_val)
    pack_count = int(pack_match.group(1)) if pack_match else 1

    if unit == 'mg':
        weight_val /= 1000
    elif unit == 'oz':
        weight_val *= 28

    total_weight = round(weight_val * pack_count, 2)
    return f"{total_weight}g", pack_count

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def match_row(row, verified_df):
    my_brand = normalize(row['My Brand'])
    my_product_raw = str(row['My Product'])
    my_product = normalize(my_product_raw)

    if not my_product:
        return ''

    # Strip brand from product
    my_product_no_brand = re.sub(r'\b' + re.escape(my_brand) + r'\b', '', my_product).strip()
    my_weight, my_pack = parse_weight_and_pack(my_product_no_brand)

    # Only compare with products that have the same brand
    brand_matches = verified_df[verified_df['Verified Brand'].str.lower() == my_brand]
    if brand_matches.empty:
        return ''

    best_match = ''
    best_score = 0

    for _, v_row in brand_matches.iterrows():
        v_prod = normalize(v_row['Verified Product'])
        verified_no_brand = re.sub(r'\b' + re.escape(my_brand) + r'\b', '', v_prod).strip()
        v_weight, v_pack = parse_weight_and_pack(verified_no_brand)

        # Skip if weights are known and don't match
        if my_weight and v_weight and my_weight != v_weight:
            continue

        score = get_similarity(my_product_no_brand, verified_no_brand)

        if score > best_score:
            best_score = score
            best_match = v_row['Verified Product']

    return best_match if best_score >= 0.5 else ''

# Run matching
verified_df = df[['Verified Product', 'Verified Brand']].dropna()
df['Matched Name'] = df.apply(lambda row: match_row(row, verified_df), axis=1)

# Save result
df.to_csv(output_path, index=False)
print(f"Matching complete. Saved to: {output_path}")

#python3 "C:\Users\inven\OneDrive\Documents\drawer-tracker-app\WeedmapsScraper\CompareLists.py"