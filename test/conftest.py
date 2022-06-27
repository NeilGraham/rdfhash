import logging
import sys
from os.path import join, dirname, normpath

sys.path.append(join(dirname(normpath(__file__)), ".."))

from rdfhash.logger import logger

logger.setLevel(logging.DEBUG)
