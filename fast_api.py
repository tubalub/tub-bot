import uvicorn
from fastapi import FastAPI, HTTPException
import logging
from service.google import fetch_google_sheet_data, SHEET_ID, DATA_RANGE

api = FastAPI()
logger = logging.getLogger(__name__)


async def start_api():
    config = uvicorn.Config(api, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


@api.post("/sheet/update")
async def update_sheet():
    try:
        data = fetch_google_sheet_data(SHEET_ID, DATA_RANGE)
        logger.info("Data fetched and processed successfully")
        return {"message": data}
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")
