from elibrarian.schemas.candidate import BookCandidate
from elibrarian.utils.isbn import extract_isbn10, extract_isbn13
from elibrarian.utils.year import is_year


def parse_file_name(file_name: str) -> BookCandidate:
    parts = [part.strip() for part in file_name.split("--")]

    remaining_parts = []

    book_candidate = BookCandidate(
        title=None,
        author=None,
        year=None,
        publisher=None,
        isbn10=None,
        isbn13=None,
    )

    for part in parts:
        isbn10 = extract_isbn10(part)
        if isbn10:
            book_candidate.isbn10 = isbn10
            continue

        isbn13 = extract_isbn13(part)
        if isbn13:
            book_candidate.isbn13 = isbn13
            continue

        if is_year(part):
            book_candidate.year = str(part)
            continue

        remaining_parts.append(part)

    if remaining_parts:
        book_candidate.title = remaining_parts.pop(0)

    if remaining_parts:
        book_candidate.author = remaining_parts.pop(0)

    return book_candidate
