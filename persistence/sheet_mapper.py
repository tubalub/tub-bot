import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


def to_name(value: Any) -> Optional[str]:
    return str(value).strip() if value else None


def to_score(value: Any) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def process_header_row(header_row: List[Any]) -> List[str]:
    titles = []
    for game in header_row:
        if not game or str(game).isspace():
            continue
        titles.append(str(game).upper())
    return titles


def process_data_row(row: List[Any],
                     max_col: int,
                     titles: List[str],
                     score_map: Dict[str, Dict[str, int]]) -> None:
    name = to_name(row[0])
    if not name:
        return

    if name not in score_map:
        score_map[name] = {}

    for col in range(1, min(len(row), max_col)):
        game = titles[col - 1] if col - 1 < len(titles) else None
        if not game:
            continue
        score = to_score(row[col])
        score_map[name][game] = score


def map_to_scores(sheet: List[List[Any]],
                  end_row_title: str) -> Dict[str, Dict[str, int]]:
    """
    Helper function to process data from Google sheets
    :param end_row_title: delimiter for the end of the data
    :param sheet: 2D array to read from
    :return: Dictionary of users -> list of scores
    """
    if not sheet:
        return {}

    score_map: Dict[str, Dict[str, int]] = {}

    titles = process_header_row(sheet[0])
    max_col = len(sheet[0])
    max_row = len(sheet)
    for i, item in enumerate(sheet):
        if end_row_title.upper() == str(item[0]).upper():
            max_row = i
            break

    for row in sheet[2:max_row]:
        if not row:
            continue
        process_data_row(row, max_col, titles, score_map)

    return score_map
