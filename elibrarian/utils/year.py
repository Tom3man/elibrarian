import re


def is_year(part: str) -> bool:

    YEAR_RE = re.compile(r"^(?:1[5-9]\d{2}|20\d{2}|21\d{2})$")

    return bool(YEAR_RE.fullmatch(part.strip()))
