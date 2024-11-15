from domain.GameScore import GameScore


def format_name(s: str) -> str:
    """
    Formats a name string by capitalizing the first word and stripping any leading or trailing whitespace.

    Args:
        s (str): The name string to format.

    Returns:
        str: The formatted name string.
    """
    s = s.strip()
    if not s:
        return s

    first_word, rest = s.split(' ', 1) if ' ' in s else (s, '')
    formatted_first_word = first_word.capitalize()
    return f"{formatted_first_word} {rest}".strip()


def get_recommendation_string(games: list[GameScore]) -> str:
    """
    Generates a formatted recommendation string for a list of games.

    Args:
        games (list[GameScore]): The list of GameScore objects.

    Returns:
        str: The formatted recommendation string.
    """
    rows = get_display_table(games)
    header = ["Rank", "Game", "Score", "Fans", "Excludes"]
    table = [header] + rows
    formatted_table = "\n".join([" | ".join(row) for row in table])
    return f"```\n{formatted_table}\n```"


def get_display_table(games: list[GameScore]) -> list[list[str]]:
    """
    Generates a display table for a list of games.

    Args:
        games (list[GameScore]): The list of GameScore objects.

    Returns:
        list[list[str]]: The display table as a list of lists of strings.
    """
    rows = []
    rank = 1
    for game in games:
        name = game.name
        score = game.score
        fans = ",".join([format_name(user.aliases[0])
                        for user in game.favored_users[:3]])
        excludes = ",".join([format_name(user.aliases[0])
                            for user in game.excluded_users])
        rows.append([rank, name, score, fans, excludes])
        rank += 1
    format_table_width(rows)
    return rows


def format_table_width(rows: list[list[str]]):
    """
    Formats the width of the columns in the display table.

    Args:
        rows (list[list[str]]): The display table as a list of lists of strings.
    """
    max_rank = 0
    max_name = 0
    max_score = 0
    max_fans = 0
    max_excludes = 0

    for row in rows:
        max_rank = max(max_rank, len(str(row[0])))
        max_name = max(max_name, len(row[1]))
        max_score = max(max_score, len(str(row[2])))
        max_fans = max(max_fans, len(row[3]))
        max_excludes = max(max_excludes, len(row[4]))

    for row in rows:
        row[0] = row[0].rjust(max_rank)
        row[1] = row[1].ljust(max_name)
        row[2] = row[2].rjust(max_score)
        row[3] = row[3].ljust(max_fans)
        row[4] = row[4].ljust(max_excludes)
