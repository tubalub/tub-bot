import asyncio
import logging

from fast_api import start_api, api

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    asyncio.run(start_api())
