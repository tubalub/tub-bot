import logging

import lightbulb

from persistence import mongo_client

loader = lightbulb.Loader()
logger = logging.getLogger(__name__)

@loader.command
class Yo(lightbulb.SlashCommand,
         name="yo",
         description="Get list of top yo sayers"):
    limit: int = lightbulb.integer("users", "Number of users to display", default=5)

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        users = mongo_client.find_users_by_yo_count(self.limit)
        logger.info(f"Found top {len(users)} users by yo count: {users}")
        await ctx.respond(self._format_user_string(users))

    def _format_user_string(self, users: list[dict[str, int]]) -> str:
        formatted_table = "\n".join([f"{user['display_name']}: {user['yo_count']}" for user in users])
        return f"```\n{formatted_table}\n```"
