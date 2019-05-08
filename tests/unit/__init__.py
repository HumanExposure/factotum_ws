"""Houses unit tests for factotum_ws.

Unit testing is a level of software testing
where individual units/components of a software are tested.
"""
import os
import importlib

for module in os.listdir(os.path.dirname(__file__)):
    if module != "__init__.py" and module[-3:] == ".py":
        importlib.import_module("." + module[:-3], "tests.unit")
del module
