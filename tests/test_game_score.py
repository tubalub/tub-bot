# test_game_score.py
import pytest

from domain.GameScore import GameScore
from domain.User import User


@pytest.fixture
def users():
    return [
        User(id="1", aliases=["user1"], games={"game1": 200}),
        User(id="2", aliases=["user2"], games={"game1": 100}),
        User(id="3", aliases=["user3"], games={"game1": 50}),
        User(id="4", aliases=["user4"], games={"game1": 0}),
    ]


def test_game_score_initialization(users):
    game_score = GameScore(name="game1", users=users)
    assert game_score.name == "game1"
    assert len(game_score.favored_users) == 3
    assert len(game_score.excluded_users) == 1


def test_get_top_users(users):
    game_score = GameScore(name="game1", users=users)
    top_users = game_score.get_top_users(2)
    assert len(top_users) == 2
    assert top_users[0].id == "1"
    assert top_users[1].id == "2"


def test_excluded_users(users):
    game_score = GameScore(name="game1", users=users)
    assert len(game_score.excluded_users) == 1
    assert game_score.excluded_users[0].id == "4"
