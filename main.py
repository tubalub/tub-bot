import os
import logging

import hikari

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"${BOT_TOKEN}")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = hikari.GatewayBot(BOT_TOKEN)


@bot.listen()
async def ping(event: hikari.MessageCreateEvent):
    logger.info(f"Received message: {event.message}")


if __name__ == "__main__":
    # Run the bot.
    bot.run()
