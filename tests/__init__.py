import logging
import sys

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_STREAM = sys.stdout

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, stream=LOG_STREAM)

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
