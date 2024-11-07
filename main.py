import asyncio
import logging

import uvicorn

from fast_api import api
from service.google import init_google
from service.hikari_bot import bot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def start_bot():
    init_google()
    await bot.start()


async def start_api():
    config = uvicorn.Config(api, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(start_bot(), start_api())

if __name__ == "__main__":
    asyncio.run(main())
