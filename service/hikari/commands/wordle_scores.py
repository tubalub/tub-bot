import logging

import lightbulb

logger = logging.getLogger(__name__)
loader = lightbulb.Loader()


@loader.command
class WordleScores(
        lightbulb.SlashCommand,
        name="search_wordle_scores",
        description="Compute historical list of wordle scores"):

    wordle_bot_id = 1211781489931452447

    @lightbulb.invoke
    async def invoke(self, context: lightbulb.Context) -> None:
        return logger.warning("Not yet implemented")

    async def _search_wordle_messages(self, context: lightbulb.Context) -> list[str]:
        return []
