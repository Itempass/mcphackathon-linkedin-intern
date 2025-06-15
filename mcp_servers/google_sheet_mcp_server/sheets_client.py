import gspread
from google.oauth2.service_account import Credentials
import os

def get_gsheets_client():
    """
    Authenticates with Google Sheets API using service account credentials
    and returns an authorized gspread client.

    Credentials are expected to be in a JSON file whose path is specified
    by the 'GOOGLE_APPLICATION_CREDENTIALS' environment variable.

    :return: An authorized gspread client.
    """
    # Define the scope for Google Sheets and Google Drive
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Get credentials path from environment variable
    creds_path = "mcp_servers/google_sheet_mcp_server/credentials.json"

    # Authenticate using service account credentials
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)

    return client

def sheet_to_markdown(worksheet: gspread.Worksheet) -> str:
    """
    Converts a worksheet to a markdown table with cell positions.
    """
    values = worksheet.get_all_values()
    if not values:
        return ""

    markdown = ""
    # Create header row
    header = [f"[{gspread.utils.rowcol_to_a1(1, i+1)}] {h}" for i, h in enumerate(values[0])]
    markdown += "| " + " | ".join(header) + " |\n"
    # Create separator
    markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"
    # Create data rows
    for r_idx, row in enumerate(values[1:], start=2):
        md_row = []
        for c_idx, cell in enumerate(row, start=1):
            cell_id = gspread.utils.rowcol_to_a1(r_idx, c_idx)
            md_row.append(f"[{cell_id}] {cell}")
        markdown += "| " + " | ".join(md_row) + " |\n"

    return markdown

def update_cell(worksheet: gspread.Worksheet, cell_id: str, value: str):
    """
    Updates a single cell in the worksheet.
    """
    worksheet.update_acell(cell_id, value)
    return {"status": "success", "message": f"Cell {cell_id} updated."}

if __name__ == '__main__':
    # Example usage:
    # 1. Make sure you have created a service account and downloaded the JSON key,
    #    and placed it at 'mcp_servers/google_sheet_mcp_server/credentials.json'.
    # 2. Share your Google Sheet with the service account's email address.
    
    # To run this example:
    # pip install -r requirements.txt
    # python mcp_servers/google_sheet_mcp_server/sheets_client.py

    try:
        gsheets_client = get_gsheets_client()
        
        # Open a spreadsheet by its ID (key) from the URL
        spreadsheet_id = "1Nsg5-g9Wrb-Ll5tcdwrsKchL9ZbE23nKmsjQRK3niIE"
        spreadsheet = gsheets_client.open_by_key(spreadsheet_id)
        
        # Get the first sheet
        sheet = spreadsheet.sheet1
        
        # --- Example of reading the sheet as markdown ---
        print("--- Reading Sheet as Markdown ---")
        markdown_table = sheet_to_markdown(sheet)
        print(markdown_table)

        # --- Example of updating a cell ---
        print("\n--- Updating Cell B2 ---")
        update_result = update_cell(sheet, "B2", "This is an updated value!")
        print(update_result)

        # --- Verify the update by reading again ---
        print("\n--- Reading Sheet Again ---")
        markdown_table = sheet_to_markdown(sheet)
        print(markdown_table)

    except gspread.exceptions.SpreadsheetNotFound:
        print("Error: Spreadsheet not found. Make sure the ID is correct and you have shared it with the service account.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your credentials file is located at 'mcp_servers/google_sheet_mcp_server/credentials.json' and the service account has access to the sheet.") 