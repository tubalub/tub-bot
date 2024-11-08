import asyncio
import logging
import os
from datetime import datetime

import hikari
import lightbulb

from fast_api import api
from persistence.mongo_client import update_yo_count
from service.google import init_google
from service.hikari import commands

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = hikari.GatewayBot(BOT_TOKEN, intents=hikari.Intents.ALL)
client = lightbulb.client_from_app(bot)
loader = lightbulb.Loader()

@api.on_event("startup")
async def start_bot():
    logger.info("starting bot and google client")
    init_google()
    asyncio.create_task(bot.start())


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    logger.info("Loading extensions")
    # Load the commands
    await client.load_extensions_from_package(commands)
    # Start the client - causing the commands to be synced with discord
    logger.info("Starting lightbulb client")
    await client.start()


@bot.listen()
async def message(event: hikari.GuildMessageCreateEvent):
    if event.message.content and event.message.content.upper(
    ) == "YO" and not event.author.is_bot:
        return await handle_yo_message(event)


async def handle_yo_message(event: hikari.GuildMessageCreateEvent):
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
