import heapq

from domain.User import User


class GameScore:
    def __init__(self, name: str, users: list[User]):
        self.name = name
        self.score = 0
        self.favored_users = []
        self.excluded_users = []

        for user in users:
            user_score = user.games[name]
            heapq.heappush(self.favored_users, (user_score, user))
            if user_score < 1:
                self.excluded_users.append(user)
            self.score += user_score

    def get_top_users(self, n: int) -> list[User]:
        return [user for _, user in heapq.nlargest(n, self.favored_users)]
