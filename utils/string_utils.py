def format_name(s: str) -> str:
    s = s.strip()
    if not s:
        return s

    first_word, rest = s.split(' ', 1) if ' ' in s else (s, '')
    formatted_first_word = first_word.capitalize()
    return f"{formatted_first_word} {rest}".strip()
