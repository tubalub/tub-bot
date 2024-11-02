# test_mongo_client.py
import mongomock
import pytest

from domain.User import User
from persistence.mongo_client import (
    create_user, read_user, update_user, delete_user,
    add_alias, remove_alias, add_game, update_game
)


@pytest.fixture
def mock_db(monkeypatch):
    # Use mongomock to create an in-memory MongoDB instance
    client = mongomock.MongoClient()
    db = client['tubalub']
    users_collection = db['users']

    # Mock the MongoClient to return the in-memory database
    monkeypatch.setattr('persistence.mongo_client.client', client)
    monkeypatch.setattr('persistence.mongo_client.db', db)
    monkeypatch.setattr('persistence.mongo_client.users_collection', users_collection)

    yield db


def test_create_user(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    user_id = create_user(user)
    assert user_id is not None
    retrieved_user = read_user("123")
    assert retrieved_user['_id'] == "123"
    assert retrieved_user['aliases'] == ["alias1"]
    assert retrieved_user['games'] == {"game1": 100}


def test_update_user(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    update_user("123", {"new_prop": 123})
    updated_user = read_user("123")
    assert updated_user['new_prop'] == 123


def test_delete_user(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    delete_user("123")
    deleted_user = read_user("123")
    assert deleted_user is None


def test_add_alias(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    add_alias("123", "alias2")
    updated_user = read_user("123")
    assert "alias2" in updated_user['aliases']


def test_remove_alias(mock_db):
    user = User(id="123", aliases=["alias1", "alias2"], games={"game1": 100})
    create_user(user)
    remove_alias("123", "alias2")
    updated_user = read_user("123")
    assert "alias2" not in updated_user['aliases']


def test_add_game(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    add_game("123", "game2", 200)
    updated_user = read_user("123")
    assert updated_user['games']["game2"] == 200


def test_update_game(mock_db):
    user = User(id="123", aliases=["alias1"], games={"game1": 100})
    create_user(user)
    update_game("123", "game1", 200)
    updated_user = read_user("123")
    assert updated_user['games']["game1"] == 200