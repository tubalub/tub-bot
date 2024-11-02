from attr import dataclass


@dataclass
class User:
    id: str
    aliases: list[str]
    games: dict[str, int]
