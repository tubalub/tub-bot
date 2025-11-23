import logging
from datetime import datetime

from hikari import GuildMessageCreateEvent, Snowflake
from hikari.api import RESTClient

from persistence.mongo.user_mongo_client import update_yo_count
from persistence.mongo.wordle_mongo_client import update_wordle_entry
from service.user_id_cache import username_cache
from service.wordle_service import parse_wordle_message

logger = logging.getLogger(__name__)


async def handle_yo_message(event: GuildMessageCreateEvent):
    logger.info(f"Received yo from {event.message.author.display_name}")
    user_count, counter = update_yo_count(event.message.author)
    total_count = counter['count']
    threshold: int = counter['threshold']
    if total_count % threshold == 0:
        start_date = datetime.fromtimestamp(counter['start_date'])
        start_date_string = start_date.strftime('%Y-%m-%d')
        now = datetime.now()
        total_days = (now - start_date).days
        average = "{:.2f}".format(counter['count'] / total_days)
        response = (f"Congrats on being the {counter['count']}th yo! "
                    f"We've averaged {average} yo's per day since I started counting on {start_date_string}. "
                    f"You're responsible for at least {user_count}.")
        await event.message.respond(response)


async def handle_wordle_result(rest: RESTClient, event: GuildMessageCreateEvent):
    logger.info(
        f"Received wordle result from {event.message.author.display_name}")
    result = await parse_wordle_message(rest, {}, event.message)
    logger.info(f"Parsed Wordle result: {result}")

    for user in result.values():
        username = user.name

        if username.isdigit():
            try:
                logger.info(
                    f"Found snowflake id for user name {username}, looking up user")
                snowflake = Snowflake(int(username))
                if snowflake in username_cache:
                    username = username_cache[snowflake]
                else:
                    logger.info(f"Looking up user for id  {username}")
                    discord_user = await event.app.rest.fetch_user(int(username))
                    username = discord_user.display_name
                    username_cache[snowflake] = username
                logger.info(f"Resolved username: {username}")
            except Exception as e:
                logger.error(f"Failed to fetch user for id {username}: {e}")
                continue

        logger.info(
            f"Updating Wordle stats for {username}: score={user.score_sum}, win={user.win_count > 0}")
        # Update the user's Wordle stats in the database
        update_wordle_entry(username, user.score_sum, user.win_count > 0)
