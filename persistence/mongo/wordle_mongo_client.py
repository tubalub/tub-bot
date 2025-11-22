from domain.Wordle import WordleUser
from persistence.mongo.mongo_client import get_collection

wordle_collection = get_collection('wordle')


def insert(document: WordleUser):
    """
    Insert a new WordleUser document into the database.

    Args:
        document: The WordleUser document to insert
    """
    wordle_collection.update_one({
        '_id': document.name
    },
        {
            '$set': {
                '_id': document.name,
                'win_count': document.win_count,
                'play_count': document.play_count,
                'score_sum': document.score_sum
            }
    }, upsert=True)


def update_wordle_entry(name: str, score: int, win: bool):
    """
    Update a user's Wordle statistics in the database.

    Increments play_count, adds the score to score_sum, and increments win_count if applicable.
    Creates a new entry if the user doesn't exist.

    Args:
        name: The user's name (document _id)
        score: The score achieved in this game
        win: Whether the user won this game
    """
    wordle_collection.update_one({
        '_id': name
    }, {
        '$inc': {
            'play_count': 1,
            'score_sum': score,
            'win_count': 1 if win else 0
        }
    }, upsert=True)


def get_avg_scores(count: int) -> list[tuple[str, float]]:
    """
    Get the top users with the lowest average scores.

    Calculates average score as score_sum / play_count for each user and returns
    the specified count of users with the lowest averages.

    Args:
        count: The maximum number of results to return

    Returns:
        List of tuples (name, average_score) sorted from lowest to highest average score
    """
    query_projection = {
        '$project': {
            '_id': 1,
            'average_score': {
                '$divide': ['$score_sum', '$play_count']
            }
        }
    }
    sort = {
        '$sort': {
            'average_score': 1
        }
    }

    results = wordle_collection.aggregate(
        [
            query_projection,
            sort,
            {
                '$limit': count
            }
        ]
    )
    return [(doc['_id'], doc['average_score']) for doc in results]


def get_winners(count: int) -> list[tuple[str, int]]:
    """
    Get the top winners by win count.

    Returns the specified count of users with the highest win_count values.

    Args:
        count: The maximum number of results to return

    Returns:
        List of tuples (name, win_count) sorted from highest to lowest win count
    """
    docs = wordle_collection.find().sort('win_count', -1).limit(count)
    return [(doc['_id'], doc['win_count']) for doc in docs]
