import logging
from datetime import datetime
import os


class DailyRotatingFileHandler(logging.FileHandler):
    def __init__(self, directory, prefix, *args, **kwargs):
        self.directory = directory
        self.prefix = prefix
        filename = self._get_filename()
        super().__init__(filename, *args, **kwargs)

    def _get_filename(self):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"{self.prefix}_{date_str}.log"
        return os.path.join(self.directory, filename)

    def emit(self, record):
        # Check if the date has changed and update the filename if necessary
        current_filename = self.baseFilename
        new_filename = self._get_filename()
        if current_filename != new_filename:
            self.stream.close()
            self.baseFilename = new_filename
            self.stream = self._open()
        super().emit(record)
