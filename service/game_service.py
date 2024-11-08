import logging
from typing import Dict, List, Tuple

from persistence.mongo_client import find_user_by_alias, add_games

logger = logging.getLogger(__name__)


def update_scores(user_scores: Dict[str, Dict[str, int]]) -> int:
    counter = 0
    for alias, scores in user_scores.items():
        user = find_user_by_alias(alias.upper())
        add_games(user["_id"], scores)
        logger.info(f"Updated scores for user {user}")
        counter += 1
    return counter
