from datetime import datetime, date
from models import db, Goal, Task


class GoalService:
    """目標服務層"""

    @staticmethod
    def create_goal(user_id, data):
        """建立新目標"""
        try:
            goal = Goal(
                user_id=user_id,
                title=data.get('title'),
                description=data.get('description', ''),
                target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data.get('target_date') else None,
                color=data.get('color', 'primary'),
                status='active'
            )
            db.session.add(goal)
            db.session.commit()
            return goal, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def update_goal(goal_id, user_id, data):
        """更新目標（含權限檢查）"""
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return None, "目標不存在或無權限更新"

            if 'title' in data:
                goal.title = data['title']
            if 'description' in data:
                goal.description = data['description']
            if 'target_date' in data:
                goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data['target_date'] else None
            if 'color' in data:
                goal.color = data['color']
            if 'status' in data:
                goal.status = data['status']

            db.session.commit()
            return goal, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_goal(goal_id, user_id):
        """刪除目標（含權限檢查）"""
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return False, "目標不存在或無權限刪除"

            db.session.delete(goal)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_user_goals(user_id, status=None):
        """獲取使用者目標（可依狀態篩選）"""
        try:
            query = Goal.query.filter_by(user_id=user_id)
            if status:
                query = query.filter_by(status=status)
            goals = query.order_by(Goal.created_at.desc()).all()
            return goals, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_goal_by_id(goal_id, user_id):
        """獲取特定目標（含權限檢查）"""
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return None, "目標不存在或無權限存取"
            return goal, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def update_goal_status(goal_id, user_id, new_status):
        """更新目標狀態"""
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return None, "目標不存在或無權限更新"

            goal.status = new_status
            db.session.commit()
            return goal, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
