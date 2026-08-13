import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

from watchdog.events import FileSystemEventHandler

from elibrarian.services.organiser import restructure_file

log = logging.getLogger(__name__)


class WatchHandler(FileSystemEventHandler, ABC):
    def __init__(self, inbox: Path, library: Path):
        self.inbox = inbox
        self.library = library

    @staticmethod
    def wait_for_file(
        filepath: Path,
        interval: float = 2,
        stable_checks: int = 3,
    ) -> bool:
        previous = None
        stable_count = 0

        while stable_count < stable_checks:
            if not filepath.exists():
                return False

            stat = filepath.stat()
            current = (stat.st_size, stat.st_mtime_ns)

            if current == previous:
                stable_count += 1
            else:
                stable_count = 0
                previous = current

            time.sleep(interval)

        return True

    def _handle_file(self, filepath: Path) -> None:
        # Ignore temporary upload files such as Nextcloud's .part files.
        if filepath.name.endswith(".part"):
            log.debug("Ignoring temporary file: %s", filepath)
            return

        # Only process files directly inside the inbox.
        if filepath.parent != self.inbox:
            return

        if not self.is_supported(filepath):
            return

        if not self.wait_for_file(filepath):
            log.warning("File disappeared before processing: %s", filepath)
            return

        self.process_file(filepath)

    def on_created(self, event) -> None:
        if event.is_directory:
            return

        self._handle_file(Path(event.src_path))

    def on_moved(self, event) -> None:
        if event.is_directory:
            return

        filepath = Path(event.dest_path)

        log.info(
            "File moved: %s -> %s",
            event.src_path,
            filepath,
        )

        self._handle_file(filepath)

    @abstractmethod
    def is_supported(self, filepath: Path) -> bool:
        """Return True if the file should be processed."""
        ...

    @abstractmethod
    def process_file(self, filepath: Path) -> None:
        """Process a detected file."""
        ...


class EbookHandler(WatchHandler):
    SUPPORTED_EXTENSIONS = {
        ".epub",
        ".pdf",
        ".mobi",
    }

    def is_supported(self, filepath: Path) -> bool:
        return filepath.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def process_file(self, filepath: Path) -> None:
        log.info("New ebook detected: %s", filepath)

        restructure_file(
            destination_path=self.library,
            input_filepath=filepath,
        )
