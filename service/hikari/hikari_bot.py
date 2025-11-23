import asyncio
import logging

import hikari
import lightbulb
from hikari import Snowflake

from service.google import init_google, BOT_TOKEN
from service.hikari import commands
from service.hikari.listener_handlers import handle_yo_message, handle_wordle_result
from service.wordle_service import initialize_wordle_messages

logger = logging.getLogger(__name__)

if BOT_TOKEN is None:
    init_google()

bot = hikari.GatewayBot(BOT_TOKEN, intents=hikari.Intents.ALL)
client = lightbulb.client_from_app(bot)


async def start_bot():
    logger.info("Starting bot")
    bot_task = asyncio.create_task(bot.start())


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    logger.info("Loading extensions")
    # Load the commands
    await client.load_extensions_from_package(commands)
    # Start the client - causing the commands to be synced with discord
    logger.info("Starting lightbulb client")
    await client.start()


@bot.listen(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    # Initialize Wordle message cache at startup
    logger.info("Lightbulb client started")
    await initialize_wordle_messages(bot)


@bot.listen()
async def message(event: hikari.GuildMessageCreateEvent):
    if _is_valid_yo_message(event):
        return await handle_yo_message(event)
    elif _is_wordle_result(event):
        return await handle_wordle_result(event)
    return None


def _is_valid_yo_message(event) -> bool:
    return event.message.content and event.message.content.upper() == "YO" and not event.author.is_bot


def _is_wordle_result(event: hikari.GuildMessageCreateEvent) -> bool:
    if event.author.id != Snowflake(1211781489931452447):
        return False

    if "Here are yesterday's results" not in event.message.content:
        return False

    return True
