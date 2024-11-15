import heapq
import logging
from typing import Dict

from domain.GameScore import GameScore
from domain.User import User
from persistence import mongo_client

logger = logging.getLogger(__name__)


def update_scores(user_scores: Dict[str, Dict[str, int]]) -> int:
    counter = 0
    for alias, scores in user_scores.items():
        user = mongo_client.find_user_by_alias(alias.upper())
        mongo_client.add_games(user["_id"], scores)
        logger.info(f"Updated scores for user {user}")
        counter += 1
    return counter


def get_top_games(users: list[User], n: int = 5) -> list[GameScore]:
    scores = []
    for game in users[0].games:
        game_score = GameScore(game, users)
        heapq.heappush(scores, (game_score.score, game_score))

    return [game_score for _, game_score in heapq.nlargest(n, scores)]
