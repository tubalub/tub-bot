import logging
import os

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

google = None
sheets = None


def init_google():
    global google, sheets
    creds: Credentials = service_account.Credentials.from_service_account_file(
        SERVICE_KEY_PATH, scopes=SCOPES)

    try:
        google = build("sheets", "v4", credentials=creds)
        sheets = google.spreadsheets()
        logger.info("Google Sheets API service created successfully")
    except HttpError as err:
        logger.error(f"HttpError occured: {err}")


def fetch_google_sheet_data(sheet_id, data_range):
    try:
        result = sheets.values().get(spreadsheetId=sheet_id, range=data_range).execute()
        values = result.get("values", [])
        score_map = map_to_scores(values, END_ROW_TITLE)
        for user, scores in score_map.items():
            logger.info(f"User: {user}, Scores: {scores}")

        return score_map
    except HttpError as err:
        logger.error(f"HttpError occurred: {err}")
        raise
