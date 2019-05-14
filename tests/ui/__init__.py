"""Houses UI tests for factotum_ws.

UI testing is a level of software testing where
the front-end is tested to work correctly against the backend.
"""
import os
import importlib

for module in os.listdir(os.path.dirname(__file__)):
    if module != "__init__.py" and module[-3:] == ".py":
        importlib.import_module("." + module[:-3], "tests.ui")
del module
