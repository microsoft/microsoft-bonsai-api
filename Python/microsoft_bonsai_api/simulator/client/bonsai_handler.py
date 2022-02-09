from collections import Counter
import logging
from logging import Logger, StreamHandler, LogRecord, Formatter
import sys
import json 


class BonsaiStreamHandler(StreamHandler):
    """
    Specialized handler for the logs that pertain to the Bonsai SDK
    """
    
    LOG_FORMAT = "%(asctime)s - [%(levelname)s] : %(message)s in %(pathname)s:%(lineno)d"
    
    INCLUDE_AZURE = False

    def __init__(self, format=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFormatter(logging.Formatter(self.LOG_FORMAT))
        self.setLevel(logging.INFO)
        self.level_counter = Counter()

    def emit(self, record: LogRecord) -> None:
        self.track(record)

        if 'azure.' not in record.name or self.INCLUDE_AZURE == True: 
            super().emit(record)
    
    def track(self, record: LogRecord):
        self.level_counter[record.levelname] += 1
        #print(self.level_counter)
