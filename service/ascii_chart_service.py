import logging
import sys
from io import StringIO

import asciibars

def format_table(data: list[dict[str, int]]) -> str:
    formatted_table = "\n".join([f"{user['display_name']}: {user['yo_count']}" for user in data])
    old_stdout = sys.stdout

    try:
        tuples = [(str(item['display_name']), int(item['yo_count'])) for item in data]
        sys.stdout = StringIO()
        spaced_tuples = adjust_spacing(tuples)
        asciibars.plot(spaced_tuples, sep_lc='|', unit='▓', max_length=40)
        table_string = sys.stdout.getvalue()
        return f"```\n{table_string if table_string else formatted_table}\n```"
    except Exception as e:
        logging.error(e)
    finally:
        sys.stdout = old_stdout

    return formatted_table


def adjust_spacing(input_tuple: list[tuple[str, int]]) -> list[tuple[str, int]]:
    max_key, max_value = 0, 0

    for key, value in input_tuple:
        max_key = max(max_key, len(key))
        max_value = max(max_value, len(str(value)))

    return [(key.ljust(max_key), value) for key, value in input_tuple]
