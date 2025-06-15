import os
import sys
from dotenv import load_dotenv
from typing import Dict
from gspread import Worksheet
from contextlib import asynccontextmanager

# Add project root to Python path to import shared models
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from fastmcp import FastMCP
# Note: Corrected the import path to be relative to the project root
from mcp_servers.google_sheet_mcp_server.sheets_client import get_gsheets_client, sheet_to_markdown, update_cell, update_sheet_row

# --- Configuration ---
load_dotenv(override=True)
# Allow configuring the sheet ID via environment variable, with a fallback
SPREADSHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1Nsg5-g9Wrb-Ll5tcdwrsKchL9ZbE23nKmsjQRK3niIE")

# Global variable to hold the worksheet object
worksheet: Worksheet = None

@asynccontextmanager
async def lifespan(app: FastMCP):
    """Initializes the gspread client and worksheet at application startup."""
    global worksheet
    print("--- Initializing Google Sheets Client ---")
    client = get_gsheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.worksheet("Sheet1")
    print("--- Google Sheets Client Initialized ---")
    yield

# --- FastMCP Application Setup ---
mcp = FastMCP("Google Sheets MCP Server", lifespan=lifespan)

# --- Tools ---

@mcp.tool(exclude_args=["user_id"])
async def read_sheet(user_id: str=None) -> str:
    """
    Reads the entire content of the Google Sheet and returns it as a markdown table.
    Each cell in the markdown table is prefixed with its cell ID (e.g., [A1]).
    """
    try:
        # The underlying function is synchronous, but FastMCP can handle it.
        return sheet_to_markdown(worksheet)
    except Exception as e:
        print(f"ERROR in read_sheet: {e}")
        # Return a meaningful error to the agent instead of crashing
        return f"An error occurred while reading the sheet: {str(e)}"
    
@mcp.tool(exclude_args=["user_id"])
async def update_sheet_cell(cell_id: str, value: str, user_id: str=None) -> Dict:
    """
    Updates a single cell in the Google Sheet. When updating the "touch points" column, make sure to include the date of each touchpoint format YYYY-MM-DD.

    Args:
        - cell_id: The ID of the cell to update (e.g., "A1", "B2").
        -value: The new value to write into the cell.
    
    Returns:
        A dictionary with the status of the operation.
    """
    print(f"Updating cell {cell_id} with value {value}")
    # The underlying function is synchronous, but FastMCP can handle it.
    return update_cell(worksheet, cell_id, value)

@mcp.tool(exclude_args=["user_id"])
async def update_row(first_cell: str, values: list[str], user_id: str=None) -> Dict:
    """
    Updates a row in the Google Sheet with a list of values. When updating the "touch points" column, make sure to include the date of each touchpoint format YYYY-MM-DD.

    Args:
        - first_cell: The starting cell of the row to update (e.g., "A1", "B2").
        - values: A list of string values to write into the cells following the first cell.
    
    Returns:
        A dictionary with the status of the operation.
    """
    print(f"Updating row starting at {first_cell} with values {values}")
    # The underlying function is synchronous, but FastMCP can handle it.
    return update_sheet_row(worksheet, first_cell, values)

# --- Server Execution ---
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    # Define a specific port for this server to avoid conflicts, with a default
    port = int(os.environ.get("MCP_GSHEETS_SERVERPORT", "8002"))
    
    print(f"🚀 Starting FastMCP Google Sheets Server on http://{host}:{port}/mcp")
    mcp.run(transport="streamable-http", host=host, port=port, path="/mcp") 