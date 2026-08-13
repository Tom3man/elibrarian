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

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        if filepath.parent != self.inbox:
            return

        if not self.wait_for_file(filepath):
            log.warning("File disappeared: %s", filepath)
            return

        self.process_file(filepath)

    @abstractmethod
    def process_file(self, filepath: Path) -> None:
        """
        Process a newly detected file.
        """
        ...


class EbookHandler(WatchHandler):
    SUPPORTED_EXTENSIONS = {
        ".epub",
        ".pdf",
        ".mobi",
    }

    def process_file(self, filepath: Path) -> None:
        if filepath.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return

        log.info("New ebook detected: %s", filepath)

        restructure_file(
            destination_path=self.library,
            input_filepath=filepath,
        )
