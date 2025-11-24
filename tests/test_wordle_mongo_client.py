# test_wordle_mongo_client.py
import mongomock
import pytest

from persistence.mongo.wordle_mongo_client import (
    update_wordle_entry,
    get_top_avg_scores,
    get_top_winners
)


@pytest.fixture
def mock_db(monkeypatch):
    # Use mongomock to create an in-memory MongoDB instance
    client = mongomock.MongoClient()
    db = client['tubalub']
    wordle_collection = db['wordle']

    # Mock the MongoClient to return the in-memory database
    monkeypatch.setattr('persistence.mongo.mongo_client.client', client)
    monkeypatch.setattr('persistence.mongo.mongo_client.db', db)
    monkeypatch.setattr(
        'persistence.mongo.wordle_mongo_client.wordle_collection', wordle_collection)

    yield db


def test_insert_wordle_entry(mock_db):
    """Test inserting a new Wordle entry."""
    update_wordle_entry("TestUser", 150, True)

    user = mock_db['wordle'].find_one({'_id': 'TestUser'})
    assert user is not None
    assert user['play_count'] == 1
    assert user['score_sum'] == 150
    assert user['win_count'] == 1


def test_update_wordle_entry_new_user(mock_db):
    """Test creating a new Wordle entry for a user."""
    update_wordle_entry("Alice", 100, True)

    user = mock_db['wordle'].find_one({'_id': 'Alice'})
    assert user is not None
    assert user['play_count'] == 1
    assert user['score_sum'] == 100
    assert user['win_count'] == 1


def test_update_wordle_entry_loss(mock_db):
    """Test updating a Wordle entry when user loses."""
    update_wordle_entry("Bob", 50, False)

    user = mock_db['wordle'].find_one({'_id': 'Bob'})
    assert user is not None
    assert user['play_count'] == 1
    assert user['score_sum'] == 50
    assert user['win_count'] == 0


def test_update_wordle_entry_multiple_games(mock_db):
    """Test updating a Wordle entry with multiple games."""
    update_wordle_entry("Charlie", 100, True)
    update_wordle_entry("Charlie", 80, True)
    update_wordle_entry("Charlie", 90, False)

    user = mock_db['wordle'].find_one({'_id': 'Charlie'})
    assert user['play_count'] == 3
    assert user['score_sum'] == 270
    assert user['win_count'] == 2


def test_get_avg_scores_single_user(mock_db):
    """Test getting average scores with a single user."""
    update_wordle_entry("User1", 100, True)

    results = get_top_avg_scores(10)

    assert len(results) == 1
    assert results[0][0] == "User1"
    assert results[0][1] - 100.0 < 0.001


def test_get_avg_scores_multiple_users(mock_db):
    """Test getting average scores with multiple users."""
    # User1: 100/1 = 100.0
    update_wordle_entry("User1", 100, True)

    # User2: 150/2 = 75.0
    update_wordle_entry("User2", 80, True)
    update_wordle_entry("User2", 70, False)

    # User3: 210/3 = 70.0
    update_wordle_entry("User3", 70, True)
    update_wordle_entry("User3", 70, True)
    update_wordle_entry("User3", 70, False)

    results = get_top_avg_scores(10)

    assert len(results) == 3
    # Should be sorted from lowest to highest
    assert results[0][0] == "User3"
    assert results[0][1] - 70.0 < 0.001
    assert results[1][0] == "User2"
    assert results[1][1] - 75.0 < 0.001
    assert results[2][0] == "User1"
    assert results[2][1] - 100.0 < 0.001


def test_get_avg_scores_with_limit(mock_db):
    """Test getting average scores with a limit."""
    update_wordle_entry("User1", 100, True)
    update_wordle_entry("User2", 80, True)
    update_wordle_entry("User3", 60, True)
    update_wordle_entry("User4", 120, True)

    results = get_top_avg_scores(2)

    assert len(results) == 2
    # Should return the 2 users with lowest average scores
    assert results[0][0] == "User3"
    assert results[1][0] == "User2"


def test_get_winners_single_user(mock_db):
    """Test getting winners with a single user."""
    update_wordle_entry("WinnerUser", 100, True)

    results = get_top_winners(10)

    assert len(results) == 1
    assert results[0][0] == "WinnerUser"
    assert results[0][1] == 1


def test_get_winners_multiple_users(mock_db):
    """Test getting winners with multiple users."""
    update_wordle_entry("Alice", 100, True)
    update_wordle_entry("Alice", 100, True)

    update_wordle_entry("Bob", 100, True)

    update_wordle_entry("Charlie", 100, True)
    update_wordle_entry("Charlie", 100, True)
    update_wordle_entry("Charlie", 100, True)

    results = get_top_winners(10)

    assert len(results) == 3
    # Should be sorted from highest to lowest win count
    assert results[0][0] == "Charlie"
    assert results[0][1] == 3
    assert results[1][0] == "Alice"
    assert results[1][1] == 2
    assert results[2][0] == "Bob"
    assert results[2][1] == 1


def test_get_winners_with_limit(mock_db):
    """Test getting winners with a limit."""
    update_wordle_entry("Alice", 100, True)
    update_wordle_entry("Alice", 100, True)

    update_wordle_entry("Bob", 100, True)

    update_wordle_entry("Charlie", 100, True)
    update_wordle_entry("Charlie", 100, True)
    update_wordle_entry("Charlie", 100, True)

    results = get_top_winners(2)

    assert len(results) == 2
    # Should return top 2 winners
    assert results[0][0] == "Charlie"
    assert results[0][1] == 3
    assert results[1][0] == "Alice"
    assert results[1][1] == 2


def test_get_winners_users_with_no_wins(mock_db):
    """Test that users with no wins are not returned."""
    update_wordle_entry("User1", 100, False)
    update_wordle_entry("User1", 100, False)

    update_wordle_entry("User2", 100, True)

    results = get_top_winners(10)

    assert len(results) == 2
    # User1 has 0 wins, User2 has 1 win
    assert results[0][0] == "User2"
    assert results[0][1] == 1
    assert results[1][0] == "User1"
    assert results[1][1] == 0
