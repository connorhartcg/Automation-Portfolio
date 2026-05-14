import time
import tkinter as tk
from tkinter import messagebox
import os
import sys
import glob
import threading
import keyboard

# Add credentials path to sys.path for import
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials')
sys.path.append(CREDENTIALS_PATH)

from sheets_auth import get_sheet  # Use gspread sheet object

# Spreadsheet and range info
SPREADSHEET_NAME = 'Private Inventory Sheet'
SHEET_NAME = 'Restock'
CELL = 'K7'
LOG_FILE = "restock_monitor_log.txt"
DOWNLOADS_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')
VAL_PREFIX = 'Valuation'
CSV_EXT = '.csv'
K8_CELL = 'K8'


def read_cell(sheet):
    value = sheet.acell(CELL).value
    return value


def write_cell(sheet, value):
    sheet.update_acell(CELL, value)


def log_true_event():
    print(f"TRUE detected at {time.strftime('%Y-%m-%d %H:%M:%S')}")


def send_hotkey():
    # Send Ctrl+Shift+Alt+I
    keyboard.send('ctrl+shift+alt+i')


def get_existing_csvs():
    return set(f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith('.csv') and f.startswith(VAL_PREFIX))


def wait_for_new_csv(existing_csvs):
    while True:
        current_csvs = set(f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith('.csv') and f.startswith(VAL_PREFIX))
        new_csvs = current_csvs - existing_csvs
        if new_csvs:
            return new_csvs.pop()
        time.sleep(2)


def handle_true(sheet):
    print(f"TRUE detected at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    sheet.update_acell(K8_CELL, 'Updating...')
    # Do not set K7 to FALSE yet
    send_hotkey()
    print("Hotkey sent. Waiting for new Valuation CSV in Downloads...")
    existing_csvs = get_existing_csvs()
    new_csv = wait_for_new_csv(existing_csvs)
    print(f"New CSV detected: {new_csv}")
    # Now set K7 to FALSE and clear K8
    write_cell(sheet, 'FALSE')
    sheet.update_acell(K8_CELL, '')
    print("Reset complete. Resuming monitoring.")


def main():
    print("Restock monitor is now monitoring... (Press Ctrl+C to stop)")
    sheet = get_sheet(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    try:
        while True:
            value = read_cell(sheet)
            if str(value).upper() == 'TRUE':
                handle_true(sheet)
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nRestock monitor stopped by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

