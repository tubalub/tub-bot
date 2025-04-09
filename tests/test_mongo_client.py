# test_mongo_client.py
import mongomock
import pytest

from domain.User import User
from persistence.EntityNotFoundError import EntityNotFoundError
from persistence.mongo_client import (
    create_user,
    update_user,
    delete_user,
    add_aliases,
    remove_alias,
    add_game,
    update_yo_count,
    find_user_by_alias,
    get_user, find_users_by_yo_count)


@pytest.fixture
def mock_db(monkeypatch):
    # Use mongomock to create an in-memory MongoDB instance
    client = mongomock.MongoClient()
    db = client['tubalub']
    users_collection = db['users']

    # Mock the MongoClient to return the in-memory database
    monkeypatch.setattr('persistence.mongo_client.client', client)
    monkeypatch.setattr('persistence.mongo_client.db', db)
    monkeypatch.setattr(
        'persistence.mongo_client.users_collection', users_collection)

    yield db


def test_create_user(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    user_id = create_user(user)
    assert user_id is not None
    retrieved_user = get_user("123")
    assert retrieved_user['_id'] == "123"
    assert retrieved_user['aliases'] == ["alias1"]
    assert retrieved_user['games'] == {"game1": 100}


def test_update_user(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    updated_user = update_user("123", {"new_prop": 123})
    assert updated_user['new_prop'] == 123


def test_delete_user(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    delete_user("123")
    with pytest.raises(EntityNotFoundError):
        get_user("123")


def test_add_alias(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    result = add_aliases("123", "alias2", "alias3")
    assert "ALIAS2" in result['aliases']
    assert "ALIAS3" in result['aliases']


def test_find_user_by_alias(mock_db):
    user = User(id="123", aliases=["alias1", "alias2"], games={"game1": 100})
    create_user(user)
    found_user = find_user_by_alias("alias1")
    assert found_user is not None
    assert found_user['_id'] == "123"
    assert "alias1" in found_user['aliases']


def test_remove_alias(mock_db):
    user = User(id="123", aliases=["alias1", "alias2"], games={"game1": 100})
    create_user(user)
    updated_user = remove_alias("123", "alias2")
    assert "alias2" not in updated_user['aliases']


def test_add_game(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    updated_user = add_game("123", "game2", 200)
    assert updated_user['games']["game2"] == 200


def test_update_yo_count(mock_db):
    # Create a mock author object
    class MockAuthor:
        def __init__(self, id, display_name):
            self.id = id
            self.display_name = display_name

    author = MockAuthor(id="123", display_name="TestUser")

    # Initialize the yo-counter document
    mock_db['users'].insert_one({"_id": "yo-counter", "count": 0})

    # Call update_yo_count and verify the results
    user_count, counter = update_yo_count(author)
    assert user_count == 1
    assert counter['count'] == 1

    # Call update_yo_count again and verify the results
    user_count, counter = update_yo_count(author)
    assert user_count == 2
    assert counter['count'] == 2


def test_get_by_yo_count(mock_db):
    mock_db['users'].insert_many(
        [{"_id": "1", "display_name": "User1", "yo_count": 1}, {"_id": "2", "display_name": "User2", "yo_count": 2}])
    result = find_users_by_yo_count(2)
    assert len(result) == 2
    assert result[0]['display_name'] == "User2"
    assert result[1]['display_name'] == "User1"
