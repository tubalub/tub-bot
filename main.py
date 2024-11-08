import asyncio
import logging.config

from fast_api import start_api, api
from service.hikari.hikari_bot import bot

logger = logging.getLogger(__name__)

api = api
bot = bot

if __name__ == "__main__":
    asyncio.run(start_api())
