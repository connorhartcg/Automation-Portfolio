import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os  # Add this import at the top
from streamlit_js_eval import streamlit_js_eval

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
    
    # Connect to both sheets
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
        result = graphics_tools_sheet.update_acell("R2", "X")
        st.success("Successfully wrote 'X' to cell R2 in Graphics Tools > DrawerData.")
    except Exception as e:
        st.error(f"Failed to write to Google Sheets: {e}")

# ---- FETCH DATA ----
def fetch_data(sheet):
    all_values = sheet.get_all_values()
    top_cells = [all_values[1][col] for col in range(1, 166, 4)]  # B2, F2, ..., FL2
    bottom_cells = [all_values[11][col] for col in range(1, 166, 4)]  # B12, F12, ..., FL12
    return top_cells, bottom_cells

top_cells, bottom_cells = fetch_data(sheet)

# Fetch dropdown values
helper_sheet = spreadsheet.worksheet("Helper Data")
dropdown_values = helper_sheet.col_values(54)[1:]  # BB is column 54, skip header

def get_lineage_options(category):
    column_map = {
        "INDICA": 18,
        "SATIVA": 42,
        "HYBRID": 30
    }
    col_num = column_map.get(category)
    if not col_num:
        return []
    values = drawer_data_sheet.col_values(col_num)[1:]  # Skip header
    return [v for v in values if v.strip()]

# ---- SQUARE TEMPLATE ----
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
    # Extract the first line (brand name is before the ':')
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
        <div style='position: relative; z-index: 1; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; text-shadow: 0 0 6px #000, 0 0 2px #000;'>
            {content}
        </div>
    </div>
    """

# ---- HTML AND CSS ----
def generate_html(top_html, bottom_html, dropdown_values):
    dropdown_options_html = "<option selected disabled>Manual Change</option>" + "".join(
        [f"<option value='{val}'>{val}</option>" for val in dropdown_values]
    )
    return '''
    <style>
        body { background-color: #111 !important; }
        .scroll-container { display: flex; flex-direction: column; padding: 20px; border-radius: 12px; margin-top: 20px; background-color: black; height: 570px; overflow: hidden; }
        .scroll-inner { display: flex; flex-direction: column; gap: 12px; overflow-x: auto; padding-bottom: 10px; }
        .square { flex: 0 0 auto; color: white; font-family: Arial, sans-serif; padding: 12px; text-align: center; font-size: 14px; font-weight: bold; border-radius: 8px; width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; transition: transform 0.2s, border 0.2s; }
        .square:hover { transform: scale(1.05); border: 2px solid white; }
        .square.red { background-color: red !important; }
        #selected-text { color: white; font-size: 18px; margin-bottom: 20px; font-family: Arial, sans-serif; font-weight: bold; }
        .fixed-dropdowns { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: #333; padding: 15px; border-radius: 12px; display: none; flex-direction: row; align-items: center; gap: 20px; }
        .fixed-dropdowns select { font-size: 16px; padding: 10px; border-radius: 8px; background-color: #222; color: white; border: 1px solid #666; min-width: 180px; }
        .action-btn { font-size: 18px; padding: 10px 16px; border-radius: 8px; border: none; margin-left: 10px; cursor: pointer; }
        .confirm-btn { background-color: green; color: white; }
        .reset-btn { background-color: red; color: white; }
        .logo-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; opacity: 0.3; z-index: 0; pointer-events: none; }
    </style>
    <div class='scroll-container'>
        <h3 style='text-align:left; color: white;'>&#x1F5C2; Drawer Flower</h3>
        <div id="selected-text"></div>
        <div class="scroll-inner">
            <div style="display: flex; gap: 10px;">''' + top_html + '''</div>
            <div style="display: flex; gap: 10px;">''' + bottom_html + '''</div>
        </div>
    </div>
    <div id="fixed-dropdowns" class="fixed-dropdowns">
        <select id="custom-dropdown">''' + dropdown_options_html + '''</select>
        <select id='lineage-dropdown' style='display:none; margin-left: 20px; min-width: 180px;'>
            <option selected disabled>Lineage Options</option>
        </select>
        <button id="confirm-btn" class="action-btn confirm-btn">✅</button>
        <button id="reset-btn" class="action-btn reset-btn">🔄</button>
    </div>
    '''

# ---- SEND SELECTION TO GOOGLE SHEETS ----
def send_to_google_sheets(selection, square_index, square_row):
    try:
        # Determine the target cell based on the square row and index
        if square_row == "TOP":
            cell = f"R{square_index + 2}"  # R2 to R43
        elif square_row == "BOTTOM":
            cell = f"S{square_index + 2}"  # S2 to S43
        else:
            st.error("Invalid square row.")
            return

        # Update the cell in the Google Sheets worksheet
        result = graphics_tools_sheet.update_acell(cell, selection)
        st.success(f"Successfully wrote '{selection}' to {cell} in Graphics Tools > DrawerData.")
    except Exception as e:
        st.error(f"Failed to write to Google Sheets: {e}")

# ---- UPDATE SHEET FUNCTION ----
def update_sheet(selected_text, selected_option):
    try:
        # Determine the row based on the selected_text (e.g., lookup logic can be added here)
        # For now, assume selected_text maps directly to a row index
        row_index = int(selected_text)  # Example: Convert text to row index
        cell = f"R{row_index}"  # Example: Update cell in column R

        # Update the cell in the Google Sheets worksheet
        result = graphics_tools_sheet.update_acell(cell, selected_option)
        st.success(f"Successfully updated sheet: {selected_text} → {selected_option}")
    except Exception as e:
        st.error(f"Failed to update sheet: {e}")

# Generate HTML for squares
top_html = "".join([make_square(item, idx) for idx, item in enumerate(top_cells)])
bottom_html = "".join([make_square(item, idx + 100) for idx, item in enumerate(bottom_cells)])

# Generate the combined HTML for the interface
combined_html = generate_html(top_html, bottom_html, dropdown_values)
import streamlit.components.v1 as components

top_html = "".join([make_square(content, i) for i, content in enumerate(top_cells)])
bottom_html = "".join([make_square(content, i + 100) for i, content in enumerate(bottom_cells)])
final_html = generate_html(top_html, bottom_html, dropdown_values)

# Prepare lineage options
indica_options = get_lineage_options("INDICA")
hybrid_options = get_lineage_options("HYBRID")
sativa_options = get_lineage_options("SATIVA")

# Inject JavaScript-friendly JSON arrays into the page
lineage_script = f"""
<script>
    window.indicaOptions = {indica_options};
    window.hybridOptions = {hybrid_options};
    window.sativaOptions = {sativa_options};
</script>
"""

# Create containers for debug and feedback messages
debug_container = st.empty()
feedback_container = st.empty()

# Get evaluation result from JavaScript
js_return = streamlit_js_eval(js_expressions=None, key="js_eval", want_output=True)

if js_return:
    debug_container.write("Debug - Received from JS:", js_return)  # Debug line
    if isinstance(js_return, dict) and "detail" in js_return:
        payload = js_return["detail"]
        debug_container.write("Debug - Payload:", payload)
        
        if payload.get("action") == "confirm":
            selected_text = payload["text"]
            selected_option = payload["option"]
            square_index = payload.get("squareIndex")
            square_row = payload.get("squareRow")
            
            debug_container.write(f"Debug - Processing: square_index={square_index}, square_row={square_row}, option={selected_option}")
            
            try:
                # Determine the target cell based on the square row and index
                if square_row == "TOP":
                    cell = f"R{square_index + 2}"  # R2 to R43
                elif square_row == "BOTTOM":
                    cell = f"S{square_index + 2}"  # S2 to S43
                else:
                    feedback_container.error("Invalid square row.")
                    st.stop()

                debug_container.write(f"Debug - Updating cell {cell} with value {selected_option}")

                # Update the cell in Google Sheets
                result = graphics_tools_sheet.update_acell(cell, selected_option)
                feedback_container.success(f"Successfully updated {cell} with '{selected_option}'")
            except Exception as e:
                feedback_container.error(f"Failed to update Google Sheets: {e}")
                debug_container.write(f"Debug - Error: {str(e)}")

# Update the JavaScript code to ensure proper message structure
components.html(f"""
<script>
window.indicaOptions = {indica_options};
window.hybridOptions = {hybrid_options};
window.sativaOptions = {sativa_options};

document.addEventListener('DOMContentLoaded', function() {{
    var squares = document.querySelectorAll('.square');
    var selectedSquare = null;
    var selectedType = null;
    var selectedSquareIndex = null;
    var selectedSquareRow = null;
    var fixedDropdowns = document.getElementById("fixed-dropdowns");
    var lineageDropdown = document.getElementById("lineage-dropdown");
    var customDropdown = document.getElementById("custom-dropdown");

    squares.forEach(function(square, idx) {{
        square.addEventListener('click', function() {{
            if (selectedSquare) {{
                selectedSquare.style.transform = '';
                selectedSquare.style.border = '';
            }}
            selectedSquare = square;
            selectedSquareIndex = idx % 100; // 0-99 for top, 0-99 for bottom
            selectedSquareRow = idx < 100 ? 'TOP' : 'BOTTOM';
            square.style.transform = 'scale(1.05)';
            square.style.border = '2px solid white';
            document.getElementById("selected-text").innerText = "Selected: " + square.innerText;
            fixedDropdowns.style.display = "flex";

            var txt = square.innerText.toUpperCase();
            var opts = [];
            if (txt.includes('INDICA')) {{
                opts = window.indicaOptions;
                selectedType = 'INDICA';
                lineageDropdown.style.display = 'inline-block';
                lineageDropdown.innerHTML = '<option selected disabled>Indica Options</option>' + opts.map(opt => `<option value="${{opt}}">${{opt}}</option>`).join('');
                customDropdown.style.display = 'inline-block';
            }} else if (txt.includes('HYBRID')) {{
                opts = window.hybridOptions;
                selectedType = 'HYBRID';
                lineageDropdown.style.display = 'inline-block';
                lineageDropdown.innerHTML = '<option selected disabled>Hybrid Options</option>' + opts.map(opt => `<option value="${{opt}}">${{opt}}</option>`).join('');
                customDropdown.style.display = 'inline-block';
            }} else if (txt.includes('SATIVA')) {{
                opts = window.sativaOptions;
                selectedType = 'SATIVA';
                lineageDropdown.style.display = 'inline-block';
                lineageDropdown.innerHTML = '<option selected disabled>Sativa Options</option>' + opts.map(opt => `<option value="${{opt}}">${{opt}}</option>`).join('');
                customDropdown.style.display = 'inline-block';
            }} else {{
                lineageDropdown.style.display = 'none';
                selectedType = null;
                customDropdown.style.display = 'inline-block';
            }}
        }});
    }});

    customDropdown.addEventListener('change', function() {{
        if (customDropdown.value !== 'Manual Change') {{
            lineageDropdown.style.display = 'none';
        }} else {{
            if (selectedType) lineageDropdown.style.display = 'inline-block';
        }}
    }});

    lineageDropdown.addEventListener('change', function() {{
        if (lineageDropdown.value && !lineageDropdown.options[lineageDropdown.selectedIndex].disabled) {{
            customDropdown.style.display = 'none';
        }} else {{
            customDropdown.style.display = 'inline-block';
        }}
    }});

    document.getElementById("reset-btn").addEventListener("click", function() {{
        if (selectedSquare) {{
            selectedSquare.style.transform = '';
            selectedSquare.style.border = '';
            selectedSquare = null;
        }}
        document.getElementById("selected-text").innerText = "";
        fixedDropdowns.style.display = "none";
        lineageDropdown.style.display = 'none';
        customDropdown.style.display = 'inline-block';
        customDropdown.selectedIndex = 0;
        lineageDropdown.selectedIndex = 0;
    }});

    document.getElementById("confirm-btn").addEventListener("click", function() {{
        if (!selectedSquare) return;
        
        const selectedText = selectedSquare.innerText;
        const selectedOption = lineageDropdown.value || customDropdown.value;
        
        if (!selectedOption || selectedOption === "Manual Change") {{
            alert("Please select a value from one of the dropdowns.");
            return;
        }}

        // Show temporary feedback
        document.getElementById("selected-text").innerText = "Updating...";

        // Instead of postMessage, set Streamlit query params to trigger rerun
        const params = new URLSearchParams(window.location.search);
        params.set('square_index', selectedSquareIndex);
        params.set('square_row', selectedSquareRow);
        params.set('selected_option', selectedOption);
        params.set('selected_text', selectedText);
        window.location.search = params.toString();
    }});
}});
</script>
""" + combined_html, height=600, scrolling=False)

# --- HANDLE CONFIRM BUTTON STREAMLIT SIDE ---
selected_tile_index = None
confirm_clicked = False

def get_selected_tile_index_and_value():
    params = st.query_params
    idx = params.get('square_index', [None])[0]
    val = params.get('selected_option', [None])[0]
    confirm = idx is not None and val is not None
    row = params.get('square_row', [None])[0]
    text = params.get('selected_text', [None])[0]
    return idx, val, confirm, row, text

selected_tile_index, dropdown_value, confirm_clicked, square_row, selected_text = get_selected_tile_index_and_value()

# Only run this block if the query params are present and not None
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
        # Add a short-lived session state flag to show the message after reload
        st.session_state['just_updated'] = f"{target_cell}|{dropdown_value}|{selected_text}"
        # Clear query params and rerun to show the message
        st.experimental_set_query_params()
        st.experimental_rerun()
    except Exception as e:
        st.session_state['just_updated_error'] = str(e)
        st.experimental_set_query_params()
        st.experimental_rerun()

# Show the success or error message after rerun
if 'just_updated' in st.session_state:
    cell, value, text = st.session_state['just_updated'].split('|', 2)
    st.success(f"Successfully updated {cell} with '{value}' from square '{text}'")
    del st.session_state['just_updated']
if 'just_updated_error' in st.session_state:
    st.error(f"Failed to update Google Sheets: {st.session_state['just_updated_error']}")
    del st.session_state['just_updated_error']

#Use below in command prompt to launch app
# cd C:\Users\inven\OneDrive\Documents\automation_and_documentation\dgt_inventory_app
# python -m streamlit run dgt_inventory_app.py