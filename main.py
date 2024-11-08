import logging.config

from fast_api import start_api, api

logger = logging.getLogger(__name__)

api = api

if __name__ == "__main__":
    start_api()
