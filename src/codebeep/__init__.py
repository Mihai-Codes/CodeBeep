"""
codebeep - AI coding agent accessible from anywhere via Beeper/Matrix.

This package provides a Matrix bot that integrates with OpenCode to allow
you to assign coding tasks from your phone.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from codebeep.bot import CodeBeepBot
from codebeep.config import Config

__all__ = ["CodeBeepBot", "Config", "__version__"]
