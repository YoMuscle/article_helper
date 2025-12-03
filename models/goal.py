from datetime import datetime
from . import db


class Goal(db.Model):
    """目標模型"""
    __tablename__ = 'goals'

    # 基本欄位
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    color = db.Column(db.String(20), default='primary')  # Bootstrap color classes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 關聯
    tasks = db.relationship('Task', backref='goal', lazy=True, cascade='all, delete-orphan')

    @property
    def completion_percentage(self):
        """計算完成百分比（基於任務數量）"""
        if not self.tasks:
            return 0
        completed_tasks = sum(1 for task in self.tasks if task.is_completed)
        return round((completed_tasks / len(self.tasks)) * 100, 1)

    @property
    def total_tasks(self):
        """總任務數"""
        return len(self.tasks)

    @property
    def completed_tasks(self):
        """已完成任務數"""
        return sum(1 for task in self.tasks if task.is_completed)

    @property
    def is_overdue(self):
        """檢查目標是否逾期"""
        if self.status == 'completed' or not self.target_date:
            return False
        return datetime.now().date() > self.target_date

    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'status': self.status,
            'color': self.color,
            'completion_percentage': self.completion_percentage,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'is_overdue': self.is_overdue,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Goal {self.title} by User {self.user_id}>'
