import logging
import shutil
from pathlib import Path

from elibrarian.models.book import OpenLibraryBook
from elibrarian.models.candidate import BookCandidate
from elibrarian.services.openlibrary import get_openlibrary_book
from elibrarian.utils.isbn import extract_isbn10, extract_isbn13
from elibrarian.utils.sanitise import sanitise_name
from elibrarian.utils.year import is_year

log = logging.getLogger(__name__)


def parse_file_name(file_name: str) -> BookCandidate:
    log.debug("Parsing filename: %s", file_name)

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
            log.debug("Extracted ISBN10: %s", isbn10)
            continue

        isbn13 = extract_isbn13(part)

        if isbn13:
            book_candidate.isbn13 = isbn13
            log.debug("Extracted ISBN13: %s", isbn13)
            continue

        if is_year(part):
            book_candidate.year = str(part)
            log.debug("Extracted year: %s", book_candidate.year)
            continue

        remaining_parts.append(part)

    if remaining_parts:
        book_candidate.title = remaining_parts.pop(0)
        log.debug("Extracted title: %s", book_candidate.title)

    if remaining_parts:
        book_candidate.author = remaining_parts.pop(0)
        log.debug("Extracted author: %s", book_candidate.author)

    return book_candidate


def build_destination(
    library: Path,
    metadata: OpenLibraryBook,
    suffix: str,
) -> Path:
    author = sanitise_name(metadata.author)
    title = sanitise_name(metadata.title)
    parts = [f"{author} -- {title}"]

    output_folder = library / author / title

    if metadata.publish_year:
        parts.append(str(metadata.publish_year))

    isbn = metadata.isbn13 or metadata.isbn10

    if isbn:
        parts.append(f"{isbn}")

    file_name = "  --  ".join(parts)

    return output_folder / f"{file_name}{suffix.lower()}"


def restructure_file(
    destination_path: Path,
    input_filepath: Path,
) -> Path | None:
    """
    Organise an ebook using Open Library metadata.
    """

    try:
        # Parse filename
        book_candidate = parse_file_name(input_filepath.name)
        log.info("Candidate: %s", book_candidate)

        # Get metadata
        openlibrary_book = get_openlibrary_book(book_candidate)

        if not openlibrary_book:
            log.info(
                "No Open Library match: %s",
                input_filepath.name,
            )
            return None

        log.info(
            "Matched: %s",
            openlibrary_book.title,
        )

        # Build complete destination path
        destination_filepath = build_destination(
            destination_path,
            openlibrary_book,
            input_filepath.suffix,
        )

        log.debug(
            "Destination: %s",
            destination_filepath,
        )

        # Don't overwrite an existing file
        if destination_filepath.exists():
            log.warning(
                "Destination already exists: %s",
                destination_filepath,
            )
            return None

        # Ensure destination directory exists
        destination_filepath.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Move file
        shutil.move(
            str(input_filepath),
            str(destination_filepath),
        )

        log.info(
            "Moved %s -> %s",
            input_filepath,
            destination_filepath,
        )

        return destination_filepath

    except Exception:
        log.exception(
            "Failed to restructure file: %s",
            input_filepath,
        )
        return None
