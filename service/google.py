import logging
import os
from typing import Dict, List, Tuple

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config
from persistence.sheet_mapper import map_to_scores

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_KEY_PATH = os.path.join(
    os.path.dirname(__file__), "../service-key.json")

SHEET_ID = config["google"]["sheets"]["sheet_id"]
DATA_RANGE = config["google"]["sheets"]["data_range"]
USER_RANGE = config["google"]["sheets"]["user_range"]
YO_RANGE = config["google"]["sheets"]["yo_range"]
END_ROW_TITLE = config["google"]["sheets"]["end_row_title"]

logger = logging.getLogger(__name__)

GOOGLE = None
SHEETS = None


def init_google():
    global GOOGLE, SHEETS
    creds: Credentials = service_account.Credentials.from_service_account_file(
        SERVICE_KEY_PATH, scopes=SCOPES)

    try:
        GOOGLE = build("sheets", "v4", credentials=creds)
        SHEETS = GOOGLE.spreadsheets()
        logger.info("Google Sheets API service created successfully")
    except HttpError as err:
        logger.error(f"HttpError occured: {err}")


def fetch_google_sheet_data(sheet_id, data_range) -> List[List[str]]:
    try:
        result = SHEETS.values().get(spreadsheetId=sheet_id, range=data_range).execute()
        return result.get("values", [])
    except HttpError as err:
        logger.error(f"HttpError occurred: {err}")
        raise
