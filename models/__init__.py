from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .document import Document
from .email_verification import EmailVerification
from .password_reset import PasswordReset
from .visitor_count import VisitorCount
from .invite_code import InviteCode
from .goal import Goal
from .task import Task
from .task_tag import TaskTag, task_tag_association
from .goal_statistics import GoalStatistics

__all__ = [
    'db', 'User', 'Document', 'EmailVerification', 'PasswordReset',
    'VisitorCount', 'InviteCode', 'Goal', 'Task', 'TaskTag',
    'task_tag_association', 'GoalStatistics'
]

