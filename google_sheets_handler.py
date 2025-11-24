# google_sheets_handler.py
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
import pandas as pd
import os
import time # For retries

# Assuming 'service_account.json' is in the same directory as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(SCRIPT_DIR, "service_account.json")

# --- Helper for Gspread Client ---
def _get_gspread_client():
    """Authenticates with gspread using the service account and returns the client."""
    try:
        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            raise FileNotFoundError(f"Service account JSON not found at: {SERVICE_ACCOUNT_PATH}")
        
        # print(f"DEBUG: Attempting to load service account from: {SERVICE_ACCOUNT_PATH}")
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH) 
        # print(f"DEBUG: Service account loaded successfully.")
        return gc
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Please ensure your Google Sheets service account JSON key file is correctly named and located.")
        return None
    except Exception as e:
        print(f"ERROR: Failed to authenticate with Google Sheets: {type(e).__name__}: {e}")
        print("Ensure Google Drive API and Google Sheets API are enabled in your GCP project.")
        return None

# --- Main Functions for Sheets Interaction ---

def get_sheet_data(main_sheet_name, worksheet_name, retries=3, delay=5):
    """
    Retrieves data from a specified worksheet within a Google Sheet as a pandas DataFrame.
    """
    gc = _get_gspread_client()
    if not gc:
        return pd.DataFrame()

    for attempt in range(retries):
        try:
            # print(f"DEBUG: Attempting to open spreadsheet: '{main_sheet_name}' (Attempt {attempt + 1}/{retries})")
            spreadsheet = gc.open(main_sheet_name)
            # print(f"DEBUG: Spreadsheet '{main_sheet_name}' opened successfully.")
            
            # print(f"DEBUG: Attempting to find worksheet: '{worksheet_name}'")
            worksheet = spreadsheet.worksheet(worksheet_name)
            # print(f"DEBUG: Found worksheet: '{worksheet_name}'")
            
            df = get_as_dataframe(worksheet)
            # print(f"DEBUG: Data retrieved from worksheet '{worksheet_name}' successfully.")
            return df
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"ERROR: Spreadsheet '{main_sheet_name}' not found. Please create it and share with service account.")
            return pd.DataFrame() # Permanent error, no need to retry
        except gspread.exceptions.WorksheetNotFound:
            print(f"ERROR: Worksheet '{worksheet_name}' not found in '{main_sheet_name}'.")
            return pd.DataFrame() # Permanent error, no need to retry
        except gspread.exceptions.APIError as e:
            if attempt < retries - 1:
                print(f"WARNING: Google Sheets API error during get_sheet_data (Attempt {attempt + 1}/{retries}): {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"CRITICAL GOOGLE SHEETS API ERROR after {retries} attempts for '{worksheet_name}': {e}")
                _print_gspread_api_hints(main_sheet_name)
                return pd.DataFrame()
        except Exception as e:
            print(f"UNEXPECTED ERROR during get_sheet_data for '{worksheet_name}': {type(e).__name__}: {e}")
            return pd.DataFrame()
    return pd.DataFrame() # Should not be reached

def update_sheet_data(dataframe, main_sheet_name, worksheet_name, retries=3, delay=5, clear_sheet=True):
    """
    Uploads/updates a pandas DataFrame to a specified Google Sheet worksheet.
    If clear_sheet is True, existing data in the worksheet will be cleared before upload.
    """
    gc = _get_gspread_client()
    if not gc:
        return

    for attempt in range(retries):
        try:
            # print(f"DEBUG: Attempting to open spreadsheet: '{main_sheet_name}' (Attempt {attempt + 1}/{retries})")
            spreadsheet = gc.open(main_sheet_name)
            # print(f"DEBUG: Spreadsheet '{main_sheet_name}' opened successfully.")
            
            # Get or create the worksheet
            # print(f"DEBUG: Attempting to find or create worksheet: '{worksheet_name}'")
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                # print(f"DEBUG: Found existing worksheet: '{worksheet_name}'")
            except gspread.exceptions.WorksheetNotFound:
                # print(f"DEBUG: Worksheet '{worksheet_name}' not found, attempting to create it...")
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=str(dataframe.shape[0] + 100), cols=str(dataframe.shape[1] + 10)) # Adjust rows/cols dynamically
                # print(f"DEBUG: Created new worksheet: '{worksheet_name}' successfully.")

            if clear_sheet:
                # print(f"DEBUG: Clearing existing data in worksheet '{worksheet_name}'...")
                worksheet.clear()
                # print(f"DEBUG: Data cleared.")

            # print(f"DEBUG: Uploading DataFrame to worksheet '{worksheet_name}'...")
            set_with_dataframe(worksheet, dataframe)
            print(f"Successfully uploaded data to Google Sheet '{main_sheet_name}', worksheet '{worksheet_name}'")
            return # Success, exit function
        except gspread.exceptions.APIError as e:
            if attempt < retries - 1:
                print(f"WARNING: Google Sheets API error during update_sheet_data (Attempt {attempt + 1}/{retries}): {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"CRITICAL GOOGLE SHEETS API ERROR after {retries} attempts for '{worksheet_name}': {e}")
                _print_gspread_api_hints(main_sheet_name)
                return
        except Exception as e:
            print(f"UNEXPECTED ERROR during Google Sheets upload for '{worksheet_name}': {type(e).__name__}: {e}")
            return

def _print_gspread_api_hints(sheet_name):
    """Helper to print common gspread API error hints."""
    print("Please ensure:")
    print("  1. Your service account JSON file is valid and for the correct project.")
    print(f"  2. The Google Sheet ('{sheet_name}') is explicitly shared with the service account's email address.")
    print("  3. The 'Google Drive API' and 'Google Sheets API' are enabled in your Google Cloud Project.")
    print("  4. The service account has 'Editor' role on the Google Cloud Project and/or the specific Google Sheet.")

# Example of how you might test this file independently
if __name__ == '__main__':
    MAIN_SPREADSHEET_NAME = "AI_Content_Optimizer_Data" # Your primary spreadsheet name

    print("Running a test of google_sheets_handler.py...")
    test_df_upload = pd.DataFrame({
        'col_upload_1': [1, 2, 3],
        'col_upload_2': ['A', 'B', 'C']
    })
    
    test_worksheet_upload = "Test_Upload_Data"
    print(f"\n--- Testing update_sheet_data for '{test_worksheet_upload}' ---")
    update_sheet_data(test_df_upload, MAIN_SPREADSHEET_NAME, test_worksheet_upload)
    print("Update test finished.")

    test_worksheet_get = "YouTube_Product_Content" # Assuming you have this worksheet
    print(f"\n--- Testing get_sheet_data for '{test_worksheet_get}' ---")
    retrieved_df = get_sheet_data(MAIN_SPREADSHEET_NAME, test_worksheet_get)
    if not retrieved_df.empty:
        print(f"Successfully retrieved data from '{test_worksheet_get}'. Head:\n{retrieved_df.head()}")
    else:
        print(f"Failed to retrieve data from '{test_worksheet_get}'.")
    print("Get test finished.")