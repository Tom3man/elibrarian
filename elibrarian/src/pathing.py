from pathlib import Path

from elibrarian.schemas.book import OpenLibraryBook
from elibrarian.utils.sanitise import sanitise_name


def build_destination(
    library: Path,
    metadata: OpenLibraryBook,
) -> Path:
    author = sanitise_name(metadata.author)
    title = sanitise_name(metadata.title)

    output_folder = library / author / title
    return output_folder
