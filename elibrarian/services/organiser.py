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
) -> Path:
    author = sanitise_name(metadata.author)
    title = sanitise_name(metadata.title)

    output_folder = library / author / title
    return output_folder


def restructure_file(
    destination_path: Path,
    input_filepath: Path,
) -> Path | None:
    """Organise an ebook using Open Library metadata.

    The function is defensive: on any failure it logs and returns None
    leaving the original file in place so a watcher can retry later.
    """

    try:
        # Parse raw filename
        book_candidate = parse_file_name(input_filepath.name)
        log.info("Candidate: %s", book_candidate)

        # Get metadata
        openlibrary_book = get_openlibrary_book(book_candidate)

        if not openlibrary_book:
            log.info("No Open Library match: %s", input_filepath.name)
            return None

        log.info("Matched: %s", openlibrary_book.title)

        # Build destination structure
        destination_folder = build_destination(
            destination_path,
            openlibrary_book,
        )

        log.debug("Destination: %s", destination_folder)

        # Don't overwrite an existing book folder
        if destination_folder.exists():
            log.warning("Destination already exists: %s", destination_folder)
            return None

        # Ensure destination directory exists
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Final destination filepath
        dest_file = destination_folder / input_filepath.name

        if dest_file.exists():
            log.warning("Destination file already exists: %s", dest_file)
            return None

        # Use shutil.move to support moves across filesystems
        shutil.move(str(input_filepath), str(dest_file))
        log.info("Moved %s -> %s", input_filepath, dest_file)

        return dest_file

    except Exception:
        log.exception("Failed to restructure file: %s", input_filepath)
        # Leave the file in place for later inspection/retry
        return None
