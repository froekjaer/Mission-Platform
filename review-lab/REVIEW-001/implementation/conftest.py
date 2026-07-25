"""conftest — put the implementation root on sys.path so `mission_platform` imports.

Run tests with:
    cd review-lab/REVIEW-001/implementation
    python -m pytest mission_platform/tests/ -v
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
