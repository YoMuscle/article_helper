from datetime import datetime
from . import db


class Document(db.Model):
    """文件模型"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    analysis_result = db.Column(db.JSON, nullable=True)  # 儲存分析結果的 JSON
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'upload_time': self.upload_time.isoformat(),
            'analysis_result': self.analysis_result
        }
    
    def __repr__(self):
        return f'<Document {self.filename} by User {self.user_id}>'

