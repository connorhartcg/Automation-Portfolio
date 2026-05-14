import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# ---- PAGE SETUP ----
st.set_page_config(page_title="🗂️ Drawer Inventory Display", layout="wide")

# ---- GOOGLE SHEETS CONNECTION ----
def connect_to_google_sheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r"C:\Users\inven\OneDrive\Documents\automation_and_documentation\dgt_inventory_app\credentials\credentials.json",
        scope
    )
    client = gspread.authorize(creds)
    inventory_sheet = client.open("Private Inventory Sheet")
    drawer_data_sheet = client.open("InventoryQuickSheet").worksheet("DrawerData")
    graphics_tools_sheet = client.open("Graphics Tools").worksheet("DrawerData")
    return inventory_sheet, drawer_data_sheet, graphics_tools_sheet

spreadsheet, drawer_data_sheet, graphics_tools_sheet = connect_to_google_sheets()
sheet = spreadsheet.worksheet("DrawerFlower")

# ---- HEADER ----
col1, col2 = st.columns([1, 8])
with col1:
    st.image(r"C:\Users\inven\OneDrive\Documents\automation_and_documentation\assets\brand_photos\Logos\DrGreenthumbs_Logo.png", width=100)
with col2:
    st.markdown("<h1 style='margin-top: 20px;'>Dr. Greenthumb's Inventory Interface</h1>", unsafe_allow_html=True)

# ---- TEST BUTTON FOR GOOGLE SHEETS WRITE ----
if st.button("Test Write to Google Sheets (R2)"):
    try:
        graphics_tools_sheet.update_acell("R2", "X")
        st.success("Successfully wrote 'X' to cell R2 in Graphics Tools > DrawerData.")
    except Exception as e:
        st.error(f"Failed to write to Google Sheets: {e}")

# ---- FETCH DATA ----
def fetch_data(sheet):
    all_values = sheet.get_all_values()
    top_cells = [all_values[1][col] for col in range(1, 166, 4)]
    bottom_cells = [all_values[11][col] for col in range(1, 166, 4)]
    return top_cells, bottom_cells

top_cells, bottom_cells = fetch_data(sheet)

# Fetch dropdown values
helper_sheet = spreadsheet.worksheet("Helper Data")
dropdown_values = helper_sheet.col_values(54)[1:]

def get_lineage_options(category):
    column_map = {
        "INDICA": 18,
        "SATIVA": 42,
        "HYBRID": 30
    }
    col_num = column_map.get(category)
    if not col_num:
        return []
    values = drawer_data_sheet.col_values(col_num)[1:]
    return [v for v in values if v.strip()]

def get_strain_color(content_upper):
    if "INDICA" in content_upper:
        return "purple"
    elif "SATIVA" in content_upper:
        return "orange"
    elif "HYBRID" in content_upper:
        return "green"
    return "lightgray"

def make_square(content, index):
    import re
    first_line = content.split('\n')[0]
    brand_name = first_line.split(':')[0].strip().replace(' ', '').upper()
    logo_filename = f"{brand_name}_Logo.png"
    logo_path = os.path.join(
        r"C:\Users\inven\OneDrive\Documents\automation_and_documentation\assets\brand_photos\Logos",
        logo_filename
    )
    logo_img_html = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            import base64
            encoded = base64.b64encode(image_file.read()).decode()
            logo_img_html = f"<img src='data:image/png;base64,{encoded}' class='logo-bg' alt='' />"
    content_upper = content.upper()
    color = "red" if "SALES FLOOR QTY" in content_upper and re.search(r"SALES FLOOR QTY:\s*(\d*)", content_upper) and int(re.search(r"SALES FLOOR QTY:\s*(\d*)", content_upper).group(1) or 0) <= 5 else get_strain_color(content_upper)
    return f"""
    <div class='square' id='square-{index}' style='background-color: {color}; position: relative; overflow: hidden;'>
        {logo_img_html}
        <div class='square-content'>
            {content}
        </div>
    </div>
    """

# Generate HTML for squares
top_html = "".join([make_square(item, idx) for idx, item in enumerate(top_cells)])
bottom_html = "".join([make_square(item, idx + 100) for idx, item in enumerate(bottom_cells)])

def generate_html(top_html, bottom_html, dropdown_values):
    dropdown_options_html = "<option selected disabled>Manual Change</option>" + "".join(
        [f"<option value='{val}'>{val}</option>" for val in dropdown_values]
    )
    return f'''
    <div class='scroll-container'>
        <h3 style='text-align:left; color: white;'>&#x1F5C2; Drawer Flower</h3>
        <div id="selected-text"></div>
        <div class="scroll-inner">
            <div style="display: flex; gap: 10px;">{top_html}</div>
            <div style="display: flex; gap: 10px;">{bottom_html}</div>
        </div>
    </div>
    <div id="fixed-dropdowns" class="fixed-dropdowns">
        <select id="custom-dropdown">{dropdown_options_html}</select>
        <select id='lineage-dropdown' style='display:none; margin-left: 20px; min-width: 180px;'>
            <option selected disabled>Lineage Options</option>
        </select>
        <button id="confirm-btn" class="action-btn confirm-btn">✅</button>
        <button id="reset-btn" class="action-btn reset-btn">🔄</button>
    </div>
    '''

combined_html = generate_html(top_html, bottom_html, dropdown_values)
import streamlit.components.v1 as components

# Prepare lineage options
indica_options = get_lineage_options("INDICA")
hybrid_options = get_lineage_options("HYBRID")
sativa_options = get_lineage_options("SATIVA")

components.html(f"""
<script>
window.indicaOptions = {indica_options};
window.hybridOptions = {hybrid_options};
window.sativaOptions = {sativa_options};
// ...existing code for event listeners and UI logic...
</script>
""" + combined_html, height=600, scrolling=False)

# --- HANDLE CONFIRM BUTTON STREAMLIT SIDE ---
def get_selected_tile_index_and_value():
    params = st.query_params
    idx = params.get('square_index', [None])[0]
    val = params.get('selected_option', [None])[0]
    row = params.get('square_row', [None])[0]
    text = params.get('selected_text', [None])[0]
    return idx, val, row, text

selected_tile_index, dropdown_value, square_row, selected_text = get_selected_tile_index_and_value()

if selected_tile_index is not None and dropdown_value is not None and square_row is not None:
    try:
        selected_tile_index = int(selected_tile_index)
        if square_row == "TOP":
            target_col = 'R'
            target_row = selected_tile_index + 2
        else:
            target_col = 'S'
            target_row = selected_tile_index + 2
        target_cell = f"{target_col}{target_row}"
        graphics_tools_sheet.update_acell(target_cell, dropdown_value)
        st.success(f"Successfully updated {target_cell} with '{dropdown_value}' from square '{selected_text}'")
        st.session_state['just_updated'] = f"{target_cell}|{dropdown_value}|{selected_text}"
        st.experimental_set_query_params()
        st.experimental_rerun()
    except Exception as e:
        st.session_state['just_updated_error'] = str(e)
        st.experimental_set_query_params()
        st.experimental_rerun()

if 'just_updated' in st.session_state:
    cell, value, text = st.session_state['just_updated'].split('|', 2)
    st.success(f"Successfully updated {cell} with '{value}' from square '{text}'")
    del st.session_state['just_updated']
if 'just_updated_error' in st.session_state:
    st.error(f"Failed to update Google Sheets: {st.session_state['just_updated_error']}")
    del st.session_state['just_updated_error']