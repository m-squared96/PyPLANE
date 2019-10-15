# This file is used to allow the test files to find the source files in source/
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import source
