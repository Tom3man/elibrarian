import logging
import shutil
from pathlib import Path

from elibrarian.src.openlibrary import get_openlibrary_book
from elibrarian.src.parser import parse_file_name
from elibrarian.src.pathing import build_destination

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
