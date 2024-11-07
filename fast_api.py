from fastapi import FastAPI, HTTPException
import logging
from service.google import fetch_google_sheet_data

api = FastAPI()
logger = logging.getLogger(__name__)


@api.post("/sheet/update")
async def update_sheet():
    try:
        data = fetch_google_sheet_data()
        logger.info("Data fetched and processed successfully")
        return {"message": data}
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")
