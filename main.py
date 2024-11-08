import asyncio
import logging

from fast_api import start_api, api
from service.hikari.hikari_bot import bot

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

api = api
bot = bot

if __name__ == "__main__":
    asyncio.run(start_api())
