from pathlib import Path

from elibrarian.src.openlibrary import get_openlibrary_book
from elibrarian.src.parser import parse_file_name
from elibrarian.src.pathing import build_destination


def restructure_file(
    destination_path: Path,
    input_filepath: Path,
) -> Path | None:
    """Organise an ebook using Open Library metadata."""

    # Parse raw filename
    book_candidate = parse_file_name(input_filepath.name)

    print(f"Candidate: {book_candidate}")

    # Get metadata
    openlibrary_book = get_openlibrary_book(book_candidate)

    if not openlibrary_book:
        print(f"No Open Library match: {input_filepath.name}")
        return None

    print(f"Matched: {openlibrary_book.title}")

    # Build destination structure
    destination_folder = build_destination(
        destination_path,
        openlibrary_book,
    )

    print(f"Destination: {destination_folder}")

    # Don't overwrite an existing book
    if destination_folder.exists():
        raise FileExistsError(f"Destination already exists: {destination_folder}")

    # Ensure destination directory exists
    destination_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Move + rename
    input_filepath.rename(destination_folder / input_filepath.name)
