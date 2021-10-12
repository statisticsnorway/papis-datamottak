import logging
from datetime import datetime

class loggFile:
  timestamp = datetime.now().strftime('pseudo_%H_%M_%S_%d_%m_%Y.log')
  
  def __init__(self, LOG_FILENAME = r"/ssb/stamme01/papis/Oppstart/"+timestamp):
    self.LOG_FILENAME = LOG_FILENAME 
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    self.formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    self.file_handler = logging.FileHandler(LOG_FILENAME)
    self.file_handler.setFormatter(self.formatter)
    self.logger.addHandler(self.file_handler)

  def getLogname(self):
    return self.LOG_FILENAME

  def getLogger(self):
    return self.logger

