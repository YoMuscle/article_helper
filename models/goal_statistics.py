from datetime import datetime
from . import db


class GoalStatistics(db.Model):
    """目標統計模型 - 每日快照"""
    __tablename__ = 'goal_statistics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    total_goals = db.Column(db.Integer, default=0)
    active_goals = db.Column(db.Integer, default=0)
    completed_goals = db.Column(db.Integer, default=0)
    archived_goals = db.Column(db.Integer, default=0)
    total_tasks = db.Column(db.Integer, default=0)
    completed_tasks = db.Column(db.Integer, default=0)
    completion_rate = db.Column(db.Float, default=0.0)  # 完成率百分比
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_user_date_stat'),
    )

    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'total_goals': self.total_goals,
            'active_goals': self.active_goals,
            'completed_goals': self.completed_goals,
            'archived_goals': self.archived_goals,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'completion_rate': self.completion_rate,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<GoalStatistics User {self.user_id} on {self.date}>'
