import logging
from datetime import datetime

from hikari import GuildMessageCreateEvent

from persistence.mongo.mongo_client import update_yo_count

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


async def handle_wordle_result(event: GuildMessageCreateEvent):
    logger.info(
        f"Received wordle result from {event.message.author.display_name}")
    logger.warning("Not yet implemented")
