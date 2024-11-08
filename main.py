import asyncio
import logging

from fast_api import start_api
from service.hikari.hikari_bot import start_bot

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def main():
    await asyncio.gather(start_bot(), start_api())

if __name__ == "__main__":
    asyncio.run(main())
