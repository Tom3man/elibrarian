import isbnlib


def extract_isbn13(value: str) -> str | None:

    for isbn in isbnlib.get_isbnlike(value):
        isbn = isbnlib.canonical(isbn)

        if isbnlib.is_isbn13(isbn):
            return isbn

    return None


def extract_isbn10(value: str) -> str | None:

    for isbn in isbnlib.get_isbnlike(value):
        isbn = isbnlib.canonical(isbn)

        if isbnlib.is_isbn10(isbn):
            return isbn

    return None


def split_isbns(
    isbns: list[str],
) -> tuple[list[str], list[str]]:
    isbn10 = []
    isbn13 = []

    for isbn in isbns:
        isbn = isbnlib.canonical(isbn)

        if not isbn:
            continue

        if isbnlib.is_isbn10(isbn):
            isbn10.append(isbn)

        elif isbnlib.is_isbn13(isbn):
            isbn13.append(isbn)

    return isbn10, isbn13
