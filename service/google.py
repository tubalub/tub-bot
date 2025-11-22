import logging
import os
from typing import Dict, List, Tuple

from google.cloud import secretmanager
from google.cloud.secretmanager_v1beta2 import SecretManagerServiceClient
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/cloud-platform"]
SERVICE_KEY_PATH = os.path.join(
    os.path.dirname(__file__), "../service-key.json")

ENV = os.getenv("ENV")

SHEET_ID = config["google"]["sheets"]["sheet_id"]
DATA_RANGE = config["google"]["sheets"]["data_range"]
USER_RANGE = config["google"]["sheets"]["user_range"]
YO_RANGE = config["google"]["sheets"]["yo_range"]
END_ROW_TITLE = config["google"]["sheets"]["end_row_title"]
PROJECT_ID = config["google"]["project_id"]
MONGO_TOKEN_KEY = config["google"]["secrets"]["MONGO_TOKEN"]
BOT_TOKEN_KEY = config["google"]["secrets"]["BOT_TOKEN"]

logger = logging.getLogger(__name__)

GOOGLE = None
SHEETS = None
SECRETS_CLIENT: SecretManagerServiceClient | None = None
BOT_TOKEN: str | None = None
MONGO_TOKEN = None


def init_google():
    logger.info("Initializing google client")
    global GOOGLE, SHEETS, SECRETS_CLIENT, BOT_TOKEN, MONGO_TOKEN

    creds: Credentials = service_account.Credentials.from_service_account_file(
        SERVICE_KEY_PATH, scopes=SCOPES)

    try:
        GOOGLE = build("sheets", "v4", credentials=creds)
        SHEETS = GOOGLE.spreadsheets()
        logger.info("Google Sheets API service created successfully")

        SECRETS_CLIENT = secretmanager.SecretManagerServiceClient(
            credentials=creds)

        if ENV == "local":
            logger.info("Using local bot token")
            BOT_TOKEN = os.getenv("LOCAL_BOT_TOKEN")
        else:
            BOT_TOKEN = get_secrets(BOT_TOKEN_KEY)

        MONGO_TOKEN = get_secrets(MONGO_TOKEN_KEY)

        if not BOT_TOKEN:
            raise ValueError("Missing bot token")
        if not MONGO_TOKEN:
            raise ValueError("Missing mongo token")
    except HttpError as err:
        logger.error(f"HttpError occured: {err}")


def get_secrets(secret_id, version_id="latest"):
    global SECRETS_CLIENT
    logger.info(f"Getting {secret_id} from Secrets Manager")
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = SECRETS_CLIENT.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def fetch_google_sheet_data(sheet_id, data_range) -> List[List[str]]:
    try:
        logger.info(f"Fetching data from {sheet_id} in range {data_range}")
        result = SHEETS.values().get(spreadsheetId=sheet_id, range=data_range).execute()
        return result.get("values", [])
    except HttpError as err:
        logger.error(f"HttpError occurred: {err}")
        raise
