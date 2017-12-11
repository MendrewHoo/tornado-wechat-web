from os.path import dirname, join, basename
import glob

pyls = [basename(f)[:-3] for f in glob.glob(join(dirname(__file__), '*.py'))]
__all__ = [f for f in pyls if f not in ('__init__', 'notfound')] + ['notfound']
