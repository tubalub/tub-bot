import unittest
from utils.string_utils import format_name, get_recommendation_string, get_display_table
from domain.GameScore import GameScore
from domain.User import User

class TestStringUtils(unittest.TestCase):

    def test_format_name(self):
        self.assertEqual(format_name(" john doe "), "John doe")
        self.assertEqual(format_name("JOHN DOE"), "John DOE")
        self.assertEqual(format_name("john"), "John")
        self.assertEqual(format_name(""), "")
        self.assertEqual(format_name(" "), "")

    def test_get_recommendation_string(self):
        user1 = User(id="1", aliases=["user1"], games={"game1": 10})
        user2 = User(id="2", aliases=["user2"], games={"game1": 5})
        user3 = User(id="3", aliases=["user3"], games={"game1": 0})
        game = GameScore(name="game1", users=[user1, user2, user3])
        games = [game]
        expected_output = (
            "```\n"
            "Rank | Game  | Score | Fans         | Excludes\n"
            "----------------------------------------------\n"
            "   1 | game1 |   15  | User1, User2 | User3   \n"
            "```"
        )
        self.assertEqual(expected_output, get_recommendation_string(games))

    def test_get_display_table(self):
        user1 = User(id="1", aliases=["user1"], games={"game1": 10})
        user2 = User(id="2", aliases=["user2"], games={"game1": 5})
        user3 = User(id="3", aliases=["user3"], games={"game1": 0})
        game = GameScore(name="game1", users=[user1, user2, user3])
        games = [game]
        expected_output = [
            ["Rank", "Game ", "Score", "Fans".ljust(12), "Excludes"],
            ["-" * 4, "-" * 5, "-" * 5, "-" * 12, "-" * 8],
            ["1".rjust(4), "game1", "15".center(5), "User1, User2", "User3".ljust(8)]
        ]
        self.assertEqual(expected_output, get_display_table(games))

if __name__ == '__main__':
    unittest.main()
