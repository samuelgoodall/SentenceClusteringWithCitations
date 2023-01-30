import os
import sys
import unittest

sys.path.append(".")
from database.base import session_factory,engine

class DatabaseTest(unittest.TestCase):
    def setUp(self) -> None: 
        self. session = session_factory()
        
    def tearDown(self) -> None:
        engine.dispose()
        os.remove("student.db")