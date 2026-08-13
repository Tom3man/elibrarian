import logging
import time

from watchdog.observers import Observer

from elibrarian.config import settings
from elibrarian.services.handlers import EbookHandler


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logger = logging.getLogger(__name__)

    handler = EbookHandler(
        inbox=settings.ebooks_inbox,
        library=settings.ebooks_library,
    )

    observer = Observer()

    observer.schedule(
        handler,
        str(settings.ebooks_inbox),
        recursive=False,
    )

    observer.start()

    logger.info(
        "Watching ebook inbox: %s",
        settings.ebooks_inbox,
    )

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
