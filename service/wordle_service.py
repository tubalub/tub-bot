# Create a predicate to filter messages from the Wordle app user
import logging
import os

import hikari
from hikari import Message, Snowflake

from config import config
from service.hikari.search import search_user_messages

logger = logging.getLogger(__name__)

if os.getenv("ENV") == "local":
    discord_config = config.get('dev', {})
    channel_id = discord_config.get('channel_id')
    wordle_user_id = discord_config.get('wordle_app_user_id')
else:
    discord_config = config.get('discord', {})
    channel_id = discord_config.get('channel_id')
    wordle_user_id = discord_config.get('wordle_app_user_id')


async def initialize_wordle_messages(bot: hikari.GatewayBot) -> None:
    """
    Initialize by fetching all Wordle bot messages at startup.

    This searches the configured Discord channel for messages from the Wordle app user
    and processes them to extract and store game scores in MongoDB.

    Args:
        bot: The Hikari bot instance
    """
    try:
        if not channel_id or not wordle_user_id:
            logger.warning(
                "Discord channel_id or wordle_app_user_id not configured")
            return

        logger.info(f"Fetching Wordle messages from channel {channel_id}")

        messages = await search_user_messages(bot, channel_id, is_wordle_message)
        logger.info(f"Cached {len(messages)} Wordle messages")

        # TODO: Process and store messages in MongoDB
        # TODO: Extract scores and player information from message content

    except Exception as e:
        logger.error(f"Failed to initialize Wordle messages: {e}")


def is_wordle_message(message: Message) -> bool:
    author_matches = message.author.id == Snowflake(wordle_user_id)
    content_matches = "Here are yesterday's results:" in message.content
    return author_matches and content_matches
