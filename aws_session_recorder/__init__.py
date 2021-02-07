"""Top-level package for aws-session-recorder."""

__author__ = """Ryan Gerstenkorn"""
__email__ = 'me@ryanjarv.sh'
__version__ = '0.1.0'

from aws_session_recorder.lib.session import Session, Base
from aws_session_recorder.lib.schema import policy, base, role, user, group, identity
