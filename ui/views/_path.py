# Centralized project path setup
# ==============================
# Import this instead of duplicating sys.path.insert in every view file.

import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

_ = None
