import sys
from os.path import join, dirname, normpath

sys.path.append(join(dirname(normpath(__file__)), ".."))

from package.__main__ import run


run()
