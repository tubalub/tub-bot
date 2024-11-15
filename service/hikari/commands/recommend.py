import asyncio
import logging

import hikari
import lightbulb
from hikari import ChannelType, Snowflake, VoiceState
from hikari.api import CacheView

from domain.User import User
from persistence import mongo_client
from persistence.mongo_client import to_user
from service import game_service
from service.hikari.hikari_bot import bot
from utils.string_utils import format_name, get_recommendation_string

loader = lightbulb.Loader()

logger = logging.getLogger(__name__)


@loader.command
class Recommend(
        lightbulb.SlashCommand,
        name="recommend",
        description="Recommend some games for users"):
    number: int = lightbulb.integer(
        "count",
        "Number of games to recommend. Default is 5.",
        default=5
    )
    users: str = lightbulb.string(
        "users",
        "Comma-seperated list of users to recommend games for.",
        default=None)

    not_found_users = []

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        users = await self._get_users(ctx)
        if not users and not self.users:
            await ctx.respond("You must be in a voice channel or provide users to recommend games for", ephemeral=True)
            return
        logger.info(f"Getting recommendations for users: {users}")
        games = game_service.get_top_games(users, self.number)
        response = ""
        if self.not_found_users:
            response += (f"I couldn't find any entries for the following users: "
                         f"{", ".join([alias for alias in self.not_found_users])}. "
                         f"Do they have entries on the google sheet?\n")
        response += get_recommendation_string(games)
        self.not_found_users = []
        await ctx.respond(response)

    async def _get_users(self, ctx: lightbulb.Context) -> list[User]:
        if self.users is not None:
            return await self._query_aliases(self.users.split(","))

        try:
            actor_voice_state = bot.cache.get_voice_state(
                ctx.guild_id, ctx.interaction.member.id)
            actor_channel = await bot.rest.fetch_channel(actor_voice_state.channel_id)
            if actor_channel.type is not ChannelType.GUILD_VOICE:
                raise AttributeError("Actor is not in a voice channel")
        except (hikari.NotFoundError, AttributeError):
            return []

        # Fetch all voice states in the guild
        voice_users: CacheView[Snowflake, VoiceState] = bot.cache.get_voice_states_view_for_channel(
            ctx.guild_id, actor_channel.id)

        return await self._query_ids(voice_users)

    async def _query_aliases(
            self,
            user_aliases: list[str]) -> list[User]:
        aliases = [user.strip().upper() for user in user_aliases]
        tasks = [
            asyncio.to_thread(
                mongo_client.find_user_by_alias,
                alias) for alias in aliases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        users: list[User] = []

        for result in results:
            try:
                users.append(to_user(result))
            except (TypeError, ValueError, mongo_client.EntityNotFoundError) as e:
                if isinstance(result, mongo_client.EntityNotFoundError):
                    formatted_str = format_name(result.query)
                    self.not_found_users.append(formatted_str)
                else:
                    logger.error(
                        f"Unhandled error when getting aliases: {e}, result: {result}")
        return users

    async def _query_ids(
            self,
            users: CacheView[Snowflake, VoiceState]) -> list[User]:
        user_ids = [user_id for user_id in users.keys()]
        # TODO: add username to not found list if query fails
        tasks = [
            asyncio.to_thread(
                mongo_client.get_user,
                str(user_id).strip().upper()) for user_id in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return await self._handle_not_found(results)

    async def _handle_not_found(
            self,
            results: list[any]) -> list[User]:
        users: list[User] = []

        for result in results:
            user = to_user(result)
            if isinstance(user, User):
                users.append(user)
            elif isinstance(result, mongo_client.EntityNotFoundError):
                formatted_str = format_name(result.query)
                self.not_found_users.append(formatted_str)
            else:
                logger.error(f"Unhandled error when getting users: {result}")

        return users
