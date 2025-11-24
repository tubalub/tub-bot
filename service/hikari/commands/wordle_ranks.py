import logging
from typing import Union

import lightbulb

from persistence.mongo.wordle_mongo_client import get_top_winners, get_top_avg_scores

loader = lightbulb.Loader()

logger = logging.getLogger(__name__)


WINS = lightbulb.Choice("wins", "wins")
AVG = lightbulb.Choice("avg", "avg")


@loader.command
class WordleRanks(
        lightbulb.SlashCommand,
        name="wordle_ranks",
        description="Compute historical list of wordle scores. Not normalized by play count."):
    count: int = lightbulb.integer(
        "count",
        "Number of top scores to return. Default is 10.",
        default=10,
        max_value=20
    )
    type: str = lightbulb.string(
        "type",
        "Type of score to compute (Wins or Avg). Default is Wins.",
        choices=[WINS, AVG],
        default=WINS
    )

    @lightbulb.invoke
    async def invoke(self, context: lightbulb.Context) -> None:
        logger.info(
            f"Received command to get wordle scores from {context.user.username} in {context.channel_id}")

        if self.type == WINS:
            logger.info(f"Computing top {self.count} wordle winners")
            winners = get_top_winners(self.count)
            await context.respond(_format_results("Most wins:", winners))
        else:
            logger.info(f"Computing top {self.count} wordle average scores")
            best_scorers = get_top_avg_scores(self.count)
            await context.respond(_format_results("Best avg:", best_scorers))

        logger.info("Finished fetching wordle ranks")


def _format_results(header_str: str, results: tuple[str, Union[int, float]]) -> str:
    if not results:
        return "No results found."
    result_str = "\n".join([f"{result[0]}: {result[1]}" for result in results])
    return f"```{header_str}\n{result_str}```"
