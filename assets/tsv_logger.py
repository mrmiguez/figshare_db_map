# assets/tsv_logger.py

import csv
import logging
from pathlib import Path


class TSVHandler(logging.Handler):

    def __init__(self, filename):
        super().__init__()

        self.filename = Path(filename)

        if not self.filename.exists():
            with open(self.filename, "w", newline="") as fh:
                writer = csv.writer(
                    fh,
                    delimiter="\t",
                    quoting=csv.QUOTE_MINIMAL
                )

                writer.writerow(
                    [
                        "timestamp",
                        "level",
                        "logger",
                        "message",
                    ]
                )

    def emit(self, record):

        try:
            with open(self.filename, "a", newline="") as fh:

                writer = csv.writer(
                    fh,
                    delimiter="\t",
                    quoting=csv.QUOTE_MINIMAL
                )

                timestamp = self.formatTime(record)

                writer.writerow(
                    [
                        timestamp,
                        record.levelname,
                        record.name,
                        getattr(record, "pid", ""),
                        getattr(record, "collection", ""),
                        record.getMessage(),
                    ]
                )

        except Exception:
            self.handleError(record)

    def formatTime(self, record):
        from datetime import datetime

        return datetime.fromtimestamp(
            record.created
        ).isoformat()
