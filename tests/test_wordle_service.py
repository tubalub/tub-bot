import pytest
import mongomock
from unittest.mock import MagicMock, patch, AsyncMock
from hikari import Message, User, Snowflake

from persistence.mongo.wordle_mongo_client import wordle_collection
# We need to mock the imports inside wordle_service before importing it
# if dependencies aren't actually installed in this environment.
# However, assuming the environment is set up, we import the functions under test.

from service.wordle_service import (
    is_wordle_message,
    parse_wordle_message,
    initialize_wordle_messages
)
from domain.Wordle import WordleUser

# --- Fixtures ---


@pytest.fixture
def mock_rest():
    """Mock RESTClient for tests."""
    return MagicMock()


@pytest.fixture
def mock_message():
    """
    Fixture that returns a factory function to create mock Hikari messages.
    """
    def _create_message(user_id: int, content: str):
        message = MagicMock(spec=Message)
        message.author = MagicMock(spec=User)
        # Ensure Snowflake compatibility for ID comparisons
        message.author.id = Snowflake(user_id)
        message.content = content
        return message
    return _create_message


@pytest.fixture
def mock_db(monkeypatch):
    """
    Creates an in-memory MongoDB instance using mongomock.
    Returns the database object.
    """
    client = mongomock.MongoClient()
    db = client['tubalub']
    # Mock the MongoClient to return the in-memory database
    monkeypatch.setattr('persistence.mongo.mongo_client.client', client)
    monkeypatch.setattr('persistence.mongo.mongo_client.db', db)
    monkeypatch.setattr(
        'persistence.mongo.wordle_mongo_client.wordle_collection', wordle_collection)
    return db

# --- Tests for is_wordle_message ---


def test_is_wordle_message_valid(mock_message):
    """Test that a correctly formatted message from the bot is accepted."""
    message = mock_message(123456789, "Here are yesterday's results:")

    # We must patch the module-level variable used in the service
    with patch('service.wordle_service.wordle_user_id', "123456789"):
        assert is_wordle_message(message) is True


def test_is_wordle_message_wrong_author(mock_message):
    """Test that a message from a different user is rejected."""
    # ID 999999999 != 123456789
    message = mock_message(999999999, "Here are yesterday's results:")

    with patch('service.wordle_service.wordle_user_id', "123456789"):
        assert is_wordle_message(message) is False


def test_is_wordle_message_wrong_content(mock_message):
    """Test that a message without the specific header is rejected."""
    message = mock_message(123456789, "Just a random message about Wordle")

    with patch('service.wordle_service.wordle_user_id', "123456789"):
        assert is_wordle_message(message) is False

# --- Tests for parse_wordle_message ---


@pytest.mark.asyncio
async def test_parse_single_winner(mock_rest, mock_message):
    """Test parsing a standard message with one winner."""
    content = """Here are yesterday's results:
    3/6: @Alice
    """
    # ID doesn't matter for parsing logic, only content
    message = mock_message(12345, content)
    user_dict = {}

    result = await parse_wordle_message(mock_rest, user_dict, message)

    assert "Alice" in result
    alice = result["Alice"]
    assert alice.play_count == 1
    assert alice.win_count == 1  # Lowest score in message (3)
    assert alice.score_sum == 3


@pytest.mark.asyncio
async def test_parse_loss(mock_rest, mock_message):
    """Test parsing a failed game (X/6)."""
    content = """Here are yesterday's results:
    X/6: @Bob
    """
    message = mock_message(12345, content)
    user_dict = {}

    result = await parse_wordle_message(mock_rest, user_dict, message)

    bob = result["Bob"]
    assert bob.play_count == 1
    assert bob.win_count == 0  # Loss is not a win
    assert bob.score_sum == 7  # 7 points for failure


@pytest.mark.asyncio
async def test_parse_mixed_results(mock_rest, mock_message):
    """
    Test logic where multiple users played.
    Alice got 3/6 (Winner of the day).
    Bob got 5/6 (Played, but didn't win the day).
    Charlie got X/6 (Failed).
    """
    content = """Here are yesterday's results:
    3/6: @Alice
    5/6: @Bob
    X/6: @Charlie
    """
    message = mock_message(12345, content)
    user_dict = {}

    result = await parse_wordle_message(mock_rest, user_dict, message)

    # Alice
    assert result["Alice"].win_count == 1  # 3 was min_attempts
    assert result["Alice"].score_sum == 3

    # Bob
    assert result["Bob"].win_count == 0  # 5 is not min_attempts (3)
    assert result["Bob"].score_sum == 5

    # Charlie
    assert result["Charlie"].win_count == 0
    assert result["Charlie"].score_sum == 7


@pytest.mark.asyncio
async def test_parse_accumulates_existing_stats(mock_rest, mock_message):
    """Test that parsing adds to existing user stats rather than overwriting."""
    user_dict = {"Alice": WordleUser(name="Alice")}
    # Pre-set stats
    user_dict["Alice"].play_count = 5
    user_dict["Alice"].win_count = 2
    user_dict["Alice"].score_sum = 20

    content = """Here are yesterday's results:
    2/6: @Alice
    """
    message = mock_message(12345, content)

    result = await parse_wordle_message(mock_rest, user_dict, message)

    alice = result["Alice"]
    assert alice.play_count == 6
    assert alice.win_count == 3  # 2/6 is a win
    assert alice.score_sum == 22


@pytest.mark.asyncio
async def test_parse_first_try_guess(mock_rest, mock_message):
    """Test the scoring logic for a 1/6 guess (maximum points)."""
    content = """Here are yesterday's results:
    1/6: @LuckyUser
    """
    message = mock_message(12345, content)
    user_dict = {}

    await parse_wordle_message(mock_rest, user_dict, message)

    user = user_dict["LuckyUser"]
    assert user.score_sum == 1


@pytest.mark.asyncio
async def test_parse_multiline_users(mock_rest, mock_message):
    """
    Test parsing when users for a specific score are spread across multiple lines.
    Example:
    1/6: @A @B
    @D @E
    2/6: @F
    """
    content = """Here are yesterday's results:
        1/6: @UserA @UserB
        @UserD @UserE
        2/6: @UserF
        """
    message = mock_message(12345, content)
    user_dict = {}

    result = await parse_wordle_message(mock_rest, user_dict, message)

    # Verify UserA (First line of 1/6)
    assert result["UserA"].score_sum == 1
    assert result["UserA"].win_count == 1  # 1/6 is min attempts

    # Verify UserB (First line of 1/6)
    assert result["UserB"].score_sum == 1
    assert result["UserB"].win_count == 1

    # Verify UserD (Second line, implies continuation of 1/6)
    assert result["UserD"].score_sum == 1
    assert result["UserD"].win_count == 1

    # Verify UserE (Second line, implies continuation of 1/6)
    assert result["UserE"].score_sum == 1
    assert result["UserE"].win_count == 1

    # Verify UserF (New score block 2/6)
    assert result["UserF"].score_sum == 2
    assert result["UserF"].win_count == 0  # 2 is not min attempts (1)


@pytest.mark.asyncio
@patch('service.wordle_service.search_user_messages')
@patch('service.wordle_service.channel_id', "general-channel")
@patch('service.wordle_service.wordle_user_id', "bot-id")
async def test_initialize_wordle_messages(mock_search, mock_message, mock_db):
    """
    Test the full initialization flow:
    1. Searches messages.
    2. Parses them.
    3. Saves results to Mongo (Verified via Mongomock).
    """
    # Setup Mock Bot
    mock_bot = MagicMock()

    # Setup Mock Messages returned by search
    msg1_content = "Here are yesterday's results:\n3/6: @UserA"
    msg2_content = "Here are yesterday's results:\n4/6: @UserA\nX/6: @UserB"

    msg1 = mock_message(12345, msg1_content)
    msg2 = mock_message(12345, msg2_content)

    mock_search.return_value = [msg1, msg2]

    # Define a side effect for the client.insert that writes to our mock_db
    # This simulates the persistence layer writing to the DB
    def fake_insert(user: WordleUser):
        # Store the user object as a dict in the mock collection
        # We assume WordleUser has a standard object structure
        mock_db.wordle_users.insert_one(vars(user))

    # Patch the client in the service to use our fake_insert
    with patch('service.wordle_service.wordle_mongo_client') as mock_client:
        mock_client.insert.side_effect = fake_insert

        # Execute
        await initialize_wordle_messages(mock_bot)

    # Verify Search was called correctly
    mock_search.assert_called_once_with(
        mock_bot, "general-channel", is_wordle_message)

    # Verify Data in Mongomock (The Real In-Memory DB)
    collection = mock_db.wordle_users

    # We expect 2 documents: UserA and UserB
    assert collection.count_documents({}) == 2

    # Fetch UserA from DB
    user_a_doc = collection.find_one({"name": "UserA"})
    assert user_a_doc is not None
    # Game 1: 3/6 (Win, 4 pts)
    # Game 2: 4/6 (Win (min attempts), 3 pts) -> Total 7 pts
    assert user_a_doc['play_count'] == 2
    assert user_a_doc['score_sum'] == 7

    # Fetch UserB from DB
    user_b_doc = collection.find_one({"name": "UserB"})
    assert user_b_doc is not None
    assert user_b_doc['play_count'] == 1
    assert user_b_doc['score_sum'] == 7


@pytest.mark.asyncio
@patch('service.wordle_service.search_user_messages')
async def test_initialize_aborts_missing_config(mock_search):
    """Test that initialization aborts gracefully if config is missing."""
    # Patch the module variables to be None
    with patch('service.wordle_service.channel_id', None):
        mock_bot = MagicMock()
        await initialize_wordle_messages(mock_bot)

        # Should not attempt to search
        mock_search.assert_not_called()
