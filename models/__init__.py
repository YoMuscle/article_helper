from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .document import Document
from .email_verification import EmailVerification
from .password_reset import PasswordReset
from .visitor_count import VisitorCount

__all__ = ['db', 'User', 'Document', 'EmailVerification', 'PasswordReset', 'VisitorCount']

