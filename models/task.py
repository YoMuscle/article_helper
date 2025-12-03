from datetime import datetime, timedelta
from . import db


class Task(db.Model):
    """任務模型"""
    __tablename__ = 'tasks'

    # 基本欄位
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False, index=True)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)  # 子任務支援
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    order_index = db.Column(db.Integer, default=0)
    reminder_sent = db.Column(db.Boolean, default=False)  # 提醒是否已發送
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 關聯
    subtasks = db.relationship(
        'Task',
        backref=db.backref('parent_task', remote_side=[id]),
        lazy=True,
        cascade='all, delete-orphan'
    )

    @property
    def is_overdue(self):
        """檢查任務是否逾期"""
        if self.is_completed or not self.due_date:
            return False
        return datetime.now().date() > self.due_date

    @property
    def days_until_due(self):
        """距離到期日的天數（負數表示已逾期）"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now().date()
        return delta.days

    @property
    def is_due_soon(self):
        """是否即將到期（3天內）"""
        if not self.due_date or self.is_completed:
            return False
        days = self.days_until_due
        return days is not None and 0 <= days <= 3

    @property
    def subtask_completion_percentage(self):
        """子任務完成百分比"""
        if not self.subtasks:
            return 100 if self.is_completed else 0
        completed = sum(1 for st in self.subtasks if st.is_completed)
        return round((completed / len(self.subtasks)) * 100, 1)

    @property
    def total_subtasks(self):
        """總子任務數"""
        return len(self.subtasks)

    @property
    def completed_subtasks(self):
        """已完成子任務數"""
        return sum(1 for st in self.subtasks if st.is_completed)

    def to_dict(self, include_subtasks=True):
        """轉換為字典格式"""
        result = {
            'id': self.id,
            'goal_id': self.goal_id,
            'parent_task_id': self.parent_task_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'priority': self.priority,
            'order_index': self.order_index,
            'is_overdue': self.is_overdue,
            'is_due_soon': self.is_due_soon,
            'days_until_due': self.days_until_due,
            'total_subtasks': self.total_subtasks,
            'completed_subtasks': self.completed_subtasks,
            'subtask_completion_percentage': self.subtask_completion_percentage,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in self.tags]
        }

        if include_subtasks and self.subtasks:
            result['subtasks'] = [st.to_dict(include_subtasks=False) for st in self.subtasks]

        return result

    def __repr__(self):
        return f'<Task {self.title}>'
