import logging

import lightbulb

from persistence.mongo import user_mongo_client
from service.ascii_chart_service import format_table

loader = lightbulb.Loader()
logger = logging.getLogger(__name__)


@loader.command
class Yo(lightbulb.SlashCommand,
         name="yo",
         description="Get list of top yo sayers"):
    limit: int = lightbulb.integer(
        "users", "Number of users to display", default=5)

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        users = user_mongo_client.find_users_by_yo_count(self.limit)
        logger.info(f"Found top {len(users)} users by yo count: {users}")
        await ctx.respond(format_table(users))
