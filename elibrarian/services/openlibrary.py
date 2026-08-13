import logging

import httpx

from elibrarian.models.book import OpenLibraryBook
from elibrarian.models.candidate import BookCandidate
from elibrarian.utils.isbn import split_isbns

log = logging.getLogger(__name__)

OPENLIBRARY_URL = "https://openlibrary.org/search.json"


def _search_openlibrary(book: BookCandidate) -> dict | None:
    """
    Search OpenLibrary for a book.

    Args:
        book (BookCandidate): The book to search for.

    Returns:
        dict: The response from the OpenLibrary API.
    """
    params = {
        "fields": ",".join(
            [
                "key",
                "title",
                "author_name",
                "publisher",
                "first_publish_year",
                "isbn",
            ]
        ),
    }

    if book.isbn13:
        params["isbn"] = book.isbn13
        log.debug("Searching OpenLibrary by ISBN13: %s", book.isbn13)
    elif book.isbn10:
        params["isbn"] = book.isbn10
        log.debug("Searching OpenLibrary by ISBN10: %s", book.isbn10)
    else:
        if book.title:
            params["title"] = book.title
            log.debug("Searching OpenLibrary by title: %s", book.title)

        if book.author:
            params["author"] = book.author
            log.debug("Searching OpenLibrary by author: %s", book.author)

        if book.year:
            params["first_publish_year"] = str(book.year)
            log.debug("Searching OpenLibrary by year: %s", book.year)

    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(OPENLIBRARY_URL, params=params)

        response.raise_for_status()
        log.debug("OpenLibrary response: %s", response.text)
        return response.json()
    except httpx.HTTPStatusError as exc:
        log.warning(
            "OpenLibrary returned HTTP %s for params=%s: %s",
            exc.response.status_code,
            params,
            exc,
        )
    except httpx.RequestError as exc:
        log.warning("OpenLibrary request failed for params=%s: %s", params, exc)
    except Exception:
        log.exception(
            "Unexpected error while querying OpenLibrary with params=%s", params
        )

    return None


def _parse_openlibrary_response(data: dict | None) -> OpenLibraryBook | None:
    if not data:
        return None

    docs = data.get("docs", [])
    if not docs:
        return None

    book = docs[0]

    isbn10, isbn13 = split_isbns(book.get("isbn", []))

    author = (book.get("author_name") or [""])[0]

    return OpenLibraryBook(
        title=book.get("title", ""),
        author=author,
        publishers=book.get("publisher", []),
        publish_year=book.get("first_publish_year"),
        isbn10=isbn10,
        isbn13=isbn13,
    )


def get_openlibrary_book(book: BookCandidate) -> OpenLibraryBook | None:
    """
    Get a book from OpenLibrary.

    Args:
        book (BookCandidate): The book to search for.

    Returns:
        OpenLibraryBook | None: The OpenLibraryBook object or None if no book was found.
    """
    response = _search_openlibrary(book)
    log.debug("OpenLibrary response: %s", response)
    return _parse_openlibrary_response(response)
