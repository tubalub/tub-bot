import asyncio
import logging

import hikari
import lightbulb
from hikari import ChannelType

from domain.User import User
from persistence import mongo_client
from persistence.mongo_client import to_user
from service.hikari.hikari_bot import bot
from utils.string_utils import format_name

loader = lightbulb.Loader()

logger = logging.getLogger(__name__)


@loader.command
class Recommend(
        lightbulb.SlashCommand,
        name="recommend",
        description="Recommend some games for users"):
    users: str = lightbulb.string(
        "users",
        "Comma-seperated list of users to recommend games for.",
        default=None)

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        users = await self._get_users(ctx)
        logger.info(f"Getting recommendations for users: {users}")
        users = [str(user.aliases[0]) for user in users]
        if not users and not self.users:
            await ctx.respond("You must be in a voice channel or provide users to recommend games for", ephemeral=True)
        else:
            await ctx.respond(f"users: {users}")

    async def _get_users(self, ctx: lightbulb.Context) -> list[User]:
        if self.users is not None:
            return await self._query_aliases(self.users.split(","), ctx)

        try:
            actor_voice_state = bot.cache.get_voice_state(
                ctx.guild_id, ctx.interaction.member.id)
            actor_channel = await bot.rest.fetch_channel(actor_voice_state.channel_id)
            if actor_channel.type is not ChannelType.GUILD_VOICE:
                raise AttributeError("Actor is not in a voice channel")
        except (hikari.NotFoundError, AttributeError):
            return []

        # Fetch all voice states in the guild
        snowflakes = bot.cache.get_voice_states_view_for_channel(
            ctx.guild_id, actor_channel.id).keys()

        return await self._query_ids([str(snowflake) for snowflake in snowflakes], ctx)

    async def _query_aliases(
            self,
            user_aliases: list[str],
            ctx: lightbulb.Context) -> list[User]:
        aliases = [user.strip().upper() for user in user_aliases]
        tasks = [
            asyncio.to_thread(
                mongo_client.find_user_by_alias,
                alias) for alias in aliases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        users: list[User] = []
        not_found: list[str] = []

        for result in results:
            try:
                users.append(to_user(result))
            except (TypeError, ValueError, mongo_client.EntityNotFoundError) as e:
                if isinstance(result, mongo_client.EntityNotFoundError):
                    formatted_str = format_name(result.query)
                    not_found.append(formatted_str)
                else:
                    logger.error(f"Unhandled error when getting aliases: {result}")

        if not_found:
            await ctx.respond(f"Could not find entries for users {not_found}")
        return users

    async def _query_ids(
            self,
            user_ids: list[str],
            ctx: lightbulb.Context) -> list[User]:
        user_id = [user_id.strip().upper() for user_id in user_ids]
        tasks = [
            asyncio.to_thread(
                mongo_client.get_user,
                alias) for alias in user_id]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return await self._handle_not_found(ctx, results)

    async def _handle_not_found(
            self,
            ctx: lightbulb.Context,
            results: list[any]) -> list[User]:
        users: list[User] = []
        not_found: list[str] = []

        for result in results:
            user = to_user(result)
            if isinstance(user, User):
                users.append(user)
            elif isinstance(result, mongo_client.EntityNotFoundError):
                formatted_str = format_name(result.query)
                not_found.append(formatted_str)
            else:
                logger.error(f"Unhandled error when getting users: {result}")

        await ctx.respond(f"Could not find entries for users {[format_name(name) for name in not_found]}")
        return users
