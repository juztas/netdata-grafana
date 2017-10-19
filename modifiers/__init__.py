""" Prepare list of all splitter plugins """
import os
import glob

MODULES = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.basename(f)[:-3] for f in MODULES if not f.endswith("__init__.py")]
