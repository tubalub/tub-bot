import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from hikari import GuildMessageCreateEvent, Message, User

from service.hikari.listener_handlers import handle_yo_message, handle_wordle_result


@pytest.fixture
def mock_event():
    """Factory to create mock GuildMessageCreateEvent."""
    def _create_event(user_id: int, display_name: str):
        event = MagicMock(spec=GuildMessageCreateEvent)
        event.message = MagicMock(spec=Message)
        event.message.author = MagicMock(spec=User)
        event.message.author.id = user_id
        event.message.author.display_name = display_name
        event.message.respond = AsyncMock()
        event.app = MagicMock()
        event.app.rest = MagicMock()
        event.app.rest.fetch_user = AsyncMock()
        return event
    return _create_event


@pytest.mark.asyncio
@patch('service.hikari.listener_handlers.update_yo_count')
async def test_handle_yo_message_no_milestone(mock_update, mock_event):
    """Test yo message handling when not at milestone."""
    event = mock_event(123, "TestUser")
    mock_update.return_value = (
        5, {'count': 99, 'threshold': 100, 'start_date': 1609459200})

    await handle_yo_message(event)

    mock_update.assert_called_once_with(event.message.author)
    event.message.respond.assert_not_called()


@pytest.mark.asyncio
@patch('service.hikari.listener_handlers.update_yo_count')
@patch('service.hikari.listener_handlers.datetime')
async def test_handle_yo_message_at_milestone(mock_datetime, mock_update, mock_event):
    """Test yo message handling at milestone threshold."""
    event = mock_event(123, "TestUser")
    mock_update.return_value = (
        10, {'count': 100, 'threshold': 100, 'start_date': 1609459200})
    mock_datetime.fromtimestamp.return_value = datetime(2021, 1, 1)
    mock_datetime.now.return_value = datetime(2021, 1, 11)

    await handle_yo_message(event)

    event.message.respond.assert_called_once()
    response = event.message.respond.call_args[0][0]
    assert "100th yo" in response
    assert "10.00 yo's per day" in response
    assert "2021-01-01" in response
    assert "at least 10" in response


@pytest.mark.asyncio
@patch('service.hikari.listener_handlers.parse_wordle_message')
@patch('service.hikari.listener_handlers.update_wordle_entry')
async def test_handle_wordle_result_simple(mock_update_entry, mock_parse, mock_event):
    """Test wordle result handling with simple username."""
    event = mock_event(123, "TestUser")
    rest = MagicMock()

    mock_user = MagicMock()
    mock_user.name = "Alice"
    mock_user.score_sum = 3
    mock_user.win_count = 1
    mock_parse.return_value = {"Alice": mock_user}

    await handle_wordle_result(rest, event)

    mock_parse.assert_called_once_with(rest, {}, event.message)
    mock_update_entry.assert_called_once_with("Alice", 3, True)


@pytest.mark.asyncio
@patch('service.hikari.listener_handlers.parse_wordle_message')
@patch('service.hikari.listener_handlers.update_wordle_entry')
async def test_handle_wordle_result_snowflake_id(mock_update_entry, mock_parse, mock_event):
    """Test wordle result handling with snowflake ID resolution."""
    event = mock_event(123, "TestUser")
    rest = MagicMock()

    mock_user = MagicMock()
    mock_user.name = "123456789"
    mock_user.score_sum = 4
    mock_user.win_count = 0
    mock_parse.return_value = {"123456789": mock_user}

    mock_discord_user = MagicMock()
    mock_discord_user.display_name = "ResolvedUser"
    event.app.rest.fetch_user.return_value = mock_discord_user

    await handle_wordle_result(rest, event)

    event.app.rest.fetch_user.assert_called_once_with(123456789)
    mock_update_entry.assert_called_once_with("ResolvedUser", 4, False)


@pytest.mark.asyncio
@patch('service.hikari.listener_handlers.parse_wordle_message')
@patch('service.hikari.listener_handlers.update_wordle_entry')
async def test_handle_wordle_result_fetch_user_fails(mock_update_entry, mock_parse, mock_event):
    """Test wordle result handling when user fetch fails."""
    event = mock_event(123, "TestUser")
    rest = MagicMock()

    mock_user = MagicMock()
    mock_user.name = "999999999"
    mock_user.score_sum = 5
    mock_user.win_count = 1
    mock_parse.return_value = {"999999999": mock_user}

    event.app.rest.fetch_user.side_effect = Exception("User not found")

    await handle_wordle_result(rest, event)

    event.app.rest.fetch_user.assert_called_once_with(999999999)
    mock_update_entry.assert_not_called()


@pytest.mark.asyncio
@patch('service.hikari.listener_handlers.parse_wordle_message')
@patch('service.hikari.listener_handlers.update_wordle_entry')
async def test_handle_wordle_result_multiple_users(mock_update_entry, mock_parse, mock_event):
    """Test wordle result handling with multiple users."""
    event = mock_event(123, "TestUser")
    rest = MagicMock()

    mock_user1 = MagicMock()
    mock_user1.name = "Alice"
    mock_user1.score_sum = 3
    mock_user1.win_count = 1

    mock_user2 = MagicMock()
    mock_user2.name = "Bob"
    mock_user2.score_sum = 7
    mock_user2.win_count = 0

    mock_parse.return_value = {"Alice": mock_user1, "Bob": mock_user2}

    await handle_wordle_result(rest, event)

    assert mock_update_entry.call_count == 2
    mock_update_entry.assert_any_call("Alice", 3, True)
    mock_update_entry.assert_any_call("Bob", 7, False)
