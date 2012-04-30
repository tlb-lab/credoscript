"""
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))

import tests.models
import tests.adaptors

testloader = unittest.TestLoader()

suite = testloader.loadTestsFromNames(['models','adaptors'])

# run unit test
unittest.TextTestRunner(verbosity=2).run(suite)