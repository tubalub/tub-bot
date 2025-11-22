import logging
import time
import typing

import hikari
from hikari import Message, Snowflake

logger = logging.getLogger(__name__)


async def search_user_messages(
        bot: hikari.GatewayBot,
        channel_id: int,
        predicate: typing.Callable[[Message], bool]
) -> list[Message]:
    """
    Search all messages in a channel that match a predicate function.

    Note: fetch_history() returns a LazyIterator that performs API calls as you iterate.

    Args:
        bot: The Hikari bot instance
        channel_id: The ID of the channel to search in
        predicate: A function that takes a Message and returns True if it matches the search criteria

    Returns:
        List of Message objects that match the predicate
    """
    start_time = time.time()
    messages = []
    try:
        channel = await bot.rest.fetch_channel(Snowflake(channel_id))

        # Verify the channel is a TextableChannel before fetching history
        if not isinstance(channel, hikari.channels.TextableChannel):
            logger.error(f"Channel {channel_id} is not a text channel")
            return messages

        async for message in channel.fetch_history():
            if predicate(message):
                messages.append(message)
    except Exception as e:
        logger.error(f"Error fetching messages from channel {channel_id}: {e}")

    elapsed_time = time.time() - start_time
    logger.info(
        f"Found {len(messages)} messages matching predicate in channel {channel_id} "
        f"(took {elapsed_time:.2f}s)")
    return messages
