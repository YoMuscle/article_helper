from datetime import datetime
from . import db


# 任務-標籤關聯表
task_tag_association = db.Table('task_tag_association',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('task_tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class TaskTag(db.Model):
    """任務標籤模型"""
    __tablename__ = 'task_tags'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='secondary')  # Bootstrap color classes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 關聯
    tasks = db.relationship(
        'Task',
        secondary=task_tag_association,
        backref=db.backref('tags', lazy='dynamic')
    )

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='unique_user_tag'),
    )

    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'task_count': self.tasks.count()
        }

    def __repr__(self):
        return f'<TaskTag {self.name}>'
