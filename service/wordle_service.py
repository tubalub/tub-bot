# Create a predicate to filter messages from the Wordle app user
import logging
import os
import re

import hikari
from hikari import Message, Snowflake
from hikari.api import RESTClient

from config import config
from domain.Wordle import WordleUser
from persistence.mongo import wordle_mongo_client
from service.hikari.search import search_user_messages
from service.user_id_cache import username_cache

logger = logging.getLogger(__name__)

if os.getenv("ENV") == "local":
    discord_config = config.get('dev', {})
    channel_id = discord_config.get('channel_id')
    wordle_user_id = discord_config.get('wordle_app_user_id')
else:
    discord_config = config.get('discord', {})
    channel_id = discord_config.get('channel_id')
    wordle_user_id = discord_config.get('wordle_app_user_id')


# Pattern to detect the start of a score block (e.g., "4/6:", "X/6:", potentially indented)
# Group 1: (\d+|X) -> The score (e.g., '4', 'X')
SCORE_START_PATTERN = re.compile(r"^\s*(\d+|X)\/6:\s*", re.MULTILINE)

# Pattern to extract names from any line:
NAME_PATTERN = re.compile(r"@([\w\s]+)")


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

        user_dict: dict[str, WordleUser] = {}

        for message in messages:
            await parse_wordle_message(bot.rest, user_dict, message)

        for wordle_user in user_dict.values():
            logger.info(f"Saving user {wordle_user}")
            wordle_mongo_client.insert(wordle_user)

    except Exception as e:
        logger.error(f"Failed to initialize Wordle messages: {e}")


def is_wordle_message(message: Message) -> bool:
    author_matches = message.author.id == Snowflake(wordle_user_id)
    content_matches = "Here are yesterday's results:" in message.content
    return author_matches and content_matches


async def parse_wordle_message(rest: RESTClient, user_dict: dict[str, WordleUser], message: Message):
    # min_attempts needed to figure out winners since we're iterating line by line
    attempts = 0
    min_attempts = 7
    logger.info(f"Processing Wordle message: {message.id}: {message.content}")

    for line in message.content.splitlines():
        logger.info(f"Processing line: {line}")
        line = line.strip()
        if not line:
            continue

        if SCORE_START_PATTERN.match(line):
            # matched score line, e.x. "4/6: @UserA @UserB"
            parsed_attempt = SCORE_START_PATTERN.search(line).group(1)
            attempts = int(parsed_attempt) if parsed_attempt.isdigit() else 7
            min_attempts = min(min_attempts, attempts)
            logger.info(f"Attempts: {attempts}, min_attempts: {min_attempts}")

        # Extract individual user names
        for name_match in NAME_PATTERN.finditer(line):
            name = name_match.group(1).strip()  # Name without '@'

            if name.isdigit():
                try:
                    logger.info(
                        f"Found snowflake id for user name {name}, looking up user")
                    snowflake = Snowflake(int(name))
                    if snowflake in username_cache:
                        name = username_cache[snowflake]
                    else:
                        logger.info(f"Looking up user for id  {name}")
                        discord_user = await rest.fetch_user(int(name))
                        name = discord_user.display_name
                        username_cache[snowflake] = name
                    logger.info(f"Resolved username: {name}")
                except Exception as e:
                    logger.error(f"Failed to fetch user for id {name}: {e}")
                    continue

            # 4. Get or initialize the WordleUser object
            user = user_dict.get(name)
            if user is None:
                user = WordleUser(name=name)
                user_dict[name] = user

            logger.info(
                f"Updating user {name} with score {attempts} and min_attempts {min_attempts}")

            # 5. Update the user stats
            logger.info(f"Incrementing play_count for user {name}")
            user.play_count += 1

            if attempts == min_attempts and attempts <= 6:
                logger.info(f"Incrementing win_count for user {name}")
                user.win_count += 1

            # TODO: consider score calculation penalty for failures or adjusted for play count
            score_increment = attempts if attempts <= 6 else 7
            logger.info(
                f"Incrementing score_sum for user {name} by {score_increment}")
            user.score_sum += score_increment

    return user_dict
