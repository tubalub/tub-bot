import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

def update_scores(user_scores: Dict[str, List[Tuple[str, int]]]):
    for alias, scores in user_scores.items():
        logger.info(f"Updating scores for user: {alias}")
    return "stub"
