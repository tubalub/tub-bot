import logging
import os

import hikari

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = hikari.GatewayBot(BOT_TOKEN)

@bot.listen()
async def ping(event: hikari.MessageCreateEvent):
    logger.info(f"Received message: {event.message}")
