import logging

from persistence.mongo.mongo_client import add_aliases

logger = logging.Logger(__name__)


def update_aliases(data: list[list[str]]) -> int:
    counter = 0
    for row in data:
        logger.info("Updating aliases for user with id: %s", row[0])
        add_aliases(row[0], *row[1:])
        counter += 1
    return counter
