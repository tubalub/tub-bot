import os
from typing import Dict

import hikari.users
from pymongo import MongoClient, ReturnDocument

from domain.User import User
from service.google import MONGO_TOKEN, init_google, get_secrets, MONGO_TOKEN_KEY

token = MONGO_TOKEN

if not token:
    init_google()
    token = get_secrets(MONGO_TOKEN_KEY)

# MongoDB connection setup
SERVICE_USER = "arbitragexiv-service-user"
CONNECTION_STRING = f"mongodb+srv://{SERVICE_USER}:{token}@tubalub.i3nux.mongodb.net/"
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
        "_id": user.id,
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
    return users_collection.find_one({"_id": user_id})


def update_user(user_id, update_data):
    """
    Update a user in the database by ID and return the updated document.

    Args:
        user_id (str): The ID of the user to be updated.
        update_data (dict): The data to update the user with.

    Returns:
        dict: The updated user document.
    """
    return users_collection.find_one_and_update(
        {"_id": user_id},
        {"$set": update_data},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def add_aliases(user_id: str, *aliases: str):
    """
    Add an alias to a user's aliases array.

    Args:
        user_id (str): The ID of the user.
        aliases (str): The alias to be added.

    Returns:
        int: The number of documents modified.
    """
    uppercased_aliases = [alias.upper() for alias in aliases]
    return users_collection.find_one_and_update(
        {"_id": user_id},
        {"$addToSet": {"aliases": {"$each": uppercased_aliases}}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def find_user_by_alias(alias: str):
    """
    Find a user by alias.

    Args:
        alias (str): The alias to search for.

    Returns:
        User: The user object retrieved from the database.
    """
    return users_collection.find_one({"aliases": {"$in": [alias]}})


def remove_alias(user_id, alias):
    """
    Remove an alias from a user's aliases array and return the updated document.

    Args:
        user_id (str): The ID of the user.
        alias (str): The alias to be removed.

    Returns:
        dict: The updated user document.
    """
    return users_collection.find_one_and_update(
        {"_id": user_id},
        {"$pull": {"aliases": alias}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def add_games(user_id: str, games: Dict[str, int]):
    """
    Add games to a user's games dictionary and return the updated document.

    Args:
        user_id (str): The ID of the user.
        games (list[tuple[str,int]): The games to be added.

    Returns:
        dict: The updated user document.
    """
    return users_collection.find_one_and_update(
        {"_id": user_id},
        {"$set": {"games": games}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def add_game(user_id, game_name, score):
    """
    Add a game to a user's games dictionary and return the updated document.

    Args:
        user_id (str): The ID of the user.
        game_name (str): The name of the game to be added.
        score (int): The score of the game.

    Returns:
        dict: The updated user document.
    """
    return users_collection.find_one_and_update(
        {"_id": user_id},
        {"$set": {f"games.{game_name}": score}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def delete_user(user_id):
    """
    Delete a user from the database by ID.

    Args:
        user_id (str): The ID of the user to be deleted.

    Returns:
        int: The number of documents deleted.
    """
    result = users_collection.delete_one({"_id": user_id})
    return result.deleted_count


def update_yo_count(author: hikari.users.User):
    """
    Update the yo count for a user and return the updated document.

    Args:
        author (object): The author object containing id and display_name.

    Returns:
        tuple: The updated yo count and the yo-counter document.
    """
    user = users_collection.find_one_and_update(
        {"_id": str(author.id)},
        {"$inc": {"yo_count": 1}, "$set": {"display_name": author.display_name}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    counter = users_collection.find_one_and_update(
        {"_id": "yo-counter"},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return user["yo_count"], counter
