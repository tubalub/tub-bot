import os

from pymongo import MongoClient
from hikari import Snowflake

from domain.User import User

# MongoDB connection setup
SERVICE_USER = "arbitragexiv-service-user"
SERVICE_PASSWORD = os.getenv("MONGO_SERVICE_PASSWORD")
CONNECTION_STRING = f"mongodb+srv://{SERVICE_USER}:{SERVICE_PASSWORD}@tubalub.i3nux.mongodb.net/"
client = MongoClient(CONNECTION_STRING)
db = client['tubalub']
users_collection = db['users']


def create_user(user) -> str:
    """
    Create a new user in the database.

    Args:
        user (User): The user object to be created.

    Returns:
        str: The ID of the newly created user.
    """
    user_dict = {
        "id": user.id,
        "aliases": user.aliases,
        "games": user.games
    }
    return users_collection.insert_one(user_dict).inserted_id


def read_user(user_id) -> User:
    """
    Read a user from the database by ID.

    Args:
        user_id (str): The ID of the user to be read.

    Returns:
        User: The user object retrieved from the database.
    """
    return users_collection.find_one({"id": user_id})


def update_user(user_id, update_data):
    """
    Update a user in the database by ID.

    Args:
        user_id (str): The ID of the user to be updated.
        update_data (dict): The data to update the user with.

    Returns:
        int: The number of documents modified.
    """
    result = users_collection.update_one(
        {"id": Snowflake(user_id)},
        {"$set": update_data}
    )
    return result.modified_count


def add_alias(user_id, alias):
    """
    Add an alias to a user's aliases array.

    Args:
        user_id (str): The ID of the user.
        alias (str): The alias to be added.

    Returns:
        int: The number of documents modified.
    """
    return update_user(user_id, {"$addToSet": {"aliases": alias}})


def remove_alias(user_id, alias):
    """
    Remove an alias from a user's aliases array.

    Args:
        user_id (str): The ID of the user.
        alias (str): The alias to be removed.

    Returns:
        int: The number of documents modified.
    """
    return update_user(user_id, {"$pull": {"aliases": alias}})


def add_game(user_id, game_name, score):
    """
    Add a game to a user's games dictionary.

    Args:
        user_id (str): The ID of the user.
        game_name (str): The name of the game to be added.
        score (int): The score of the game.

    Returns:
        int: The number of documents modified.
    """
    return update_user(
        user_id,
        {"$set": {f"games.{game_name}": score}}
    )


def update_game(user_id, game_name, score):
    """
    Update the score of a game in a user's games dictionary.

    Args:
        user_id (str): The ID of the user.
        game_name (str): The name of the game to be updated.
        score (int): The new score of the game.

    Returns:
        int: The number of documents modified.
    """
    if not read_user(user_id).games.get(game_name):
        return add_game(user_id, game_name, score)
    else:
        return update_user(
            user_id,
            {"$set": {f"games.{game_name}": score}}
        )


def delete_user(user_id):
    """
    Delete a user from the database by ID.

    Args:
        user_id (str): The ID of the user to be deleted.

    Returns:
        int: The number of documents deleted.
    """
    result = users_collection.delete_one({"id": user_id})
    return result.deleted_count