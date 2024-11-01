from hikari import Snowflake

class User:
    id: Snowflake
    aliases: list[str]
    games: dict[str, int]
