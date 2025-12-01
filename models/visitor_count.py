from . import db
from datetime import datetime


class VisitorCount(db.Model):
    """訪客計數模型 - 記錄網站總訪客人次"""
    __tablename__ = 'visitor_count'
    
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_count(cls):
        """取得目前訪客總數"""
        record = cls.query.first()
        if record:
            return record.count
        return 0
    
    @classmethod
    def increment(cls):
        """增加訪客計數並返回新的計數值"""
        record = cls.query.first()
        if not record:
            # 如果還沒有記錄，創建一個
            record = cls(count=1)
            db.session.add(record)
        else:
            record.count += 1
        
        db.session.commit()
        return record.count
    
    def __repr__(self):
        return f'<VisitorCount {self.count}>'

