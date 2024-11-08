from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
import logging

from persistence.sheet_mapper import map_to_scores
from service.game_service import update_scores
from service.google import fetch_google_sheet_data, SHEET_ID, DATA_RANGE, USER_RANGE, END_ROW_TITLE
from service.hikari.hikari_bot import start_bot, bot
from service.user_service import update_aliases

api = FastAPI()
logger = logging.getLogger(__name__)


async def start_api():
    config = uvicorn.Config(api, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting bot")
    await start_bot()
    yield
    logger.info("Shutting down bot")
    await bot.close()

api = FastAPI(lifespan=lifespan)


@api.post("/sheet/update")
async def update_sheet():
    try:
        success = 0
        logger.info("Reading updated user sheet")
        user_data = fetch_google_sheet_data(SHEET_ID, USER_RANGE)
        logger.debug(user_data)
        count = update_aliases(user_data)
        logger.info(f"Updated {count} user aliases")
        success += 1

        logger.info("Reading updated data sheet")
        score_data = fetch_google_sheet_data(SHEET_ID, DATA_RANGE)
        score_map = map_to_scores(score_data, END_ROW_TITLE)
        count = update_scores(score_map)
        logger.info(f"Updated {count} user scores")
        success += 1

        return {"message": f"{success} successful operations"}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500,
                            detail=f"Error updating score data: {e}")
