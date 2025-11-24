import logging

import hikari
import lightbulb

from service.hikari.hikari_bot import bot
from service.wordle_service import initialize_wordle_messages

loader = lightbulb.Loader()

logger = logging.getLogger(__name__)


@loader.command
class WordleReload(
        lightbulb.SlashCommand,
        name="wordle_reload",
        description="Force reload wordle scores.",
        default_member_permissions=hikari.Permissions.NONE):

    @lightbulb.invoke
    async def invoke(self, context: lightbulb.Context) -> None:
        logger.info(
            f"Received command to reload wordle scores from {context.user.username} in {context.channel_id}")
        await context.defer(ephemeral=True)

        response = await context.respond("Reloading wordle scores. This can take a while.", ephemeral=True)

        await initialize_wordle_messages(bot)

        await context.edit_response(response, "Reloaded wordle scores successfully.")
