"""Houses integration tests for factotum_ws.

Integration testing is a level of software testing where
individual software modules are combined and tested as a group.
"""
import os
import importlib

for module in os.listdir(os.path.dirname(__file__)):
    if module != "__init__.py" and module[-3:] == ".py":
        importlib.import_module("." + module[:-3], "tests.integration")
del module
