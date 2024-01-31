import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set log level to DEBUG
console = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
