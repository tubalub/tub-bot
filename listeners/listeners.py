import logging

import hikari

from main import bot

logger = logging.getLogger(__name__)

@bot.listen()
async def ping(event: hikari.MessageCreateEvent):
    logger.info(f"Received message: {event.message}")
