from datetime import datetime, date, timedelta
from models import db, Task, Goal, TaskTag, task_tag_association


class TaskService:
    """任務服務層"""

    @staticmethod
    def create_task(goal_id, user_id, data):
        """建立新任務"""
        try:
            # 檢查目標是否屬於該使用者
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return None, "目標不存在或無權限"

            # 獲取最大 order_index
            max_order = db.session.query(db.func.max(Task.order_index)).filter_by(goal_id=goal_id).scalar() or 0

            task = Task(
                goal_id=goal_id,
                parent_task_id=data.get('parent_task_id'),
                title=data.get('title'),
                description=data.get('description', ''),
                due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
                priority=data.get('priority', 'medium'),
                order_index=max_order + 1
            )
            db.session.add(task)
            db.session.flush()  # 獲取 task.id

            # 處理標籤
            if 'tag_ids' in data and data['tag_ids']:
                tags = TaskTag.query.filter(
                    TaskTag.id.in_(data['tag_ids']),
                    TaskTag.user_id == user_id
                ).all()
                task.tags.extend(tags)

            db.session.commit()
            return task, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def update_task(task_id, user_id, data):
        """更新任務（含權限檢查）"""
        try:
            task = Task.query.join(Goal).filter(
                Task.id == task_id,
                Goal.user_id == user_id
            ).first()
            if not task:
                return None, "任務不存在或無權限更新"

            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'due_date' in data:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data['due_date'] else None
            if 'priority' in data:
                task.priority = data['priority']

            # 更新標籤
            if 'tag_ids' in data:
                task.tags = []
                if data['tag_ids']:
                    tags = TaskTag.query.filter(
                        TaskTag.id.in_(data['tag_ids']),
                        TaskTag.user_id == user_id
                    ).all()
                    task.tags.extend(tags)

            db.session.commit()
            return task, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_task(task_id, user_id):
        """刪除任務（含權限檢查）"""
        try:
            task = Task.query.join(Goal).filter(
                Task.id == task_id,
                Goal.user_id == user_id
            ).first()
            if not task:
                return False, "任務不存在或無權限刪除"

            db.session.delete(task)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def toggle_task_completion(task_id, user_id):
        """切換任務完成狀態"""
        try:
            task = Task.query.join(Goal).filter(
                Task.id == task_id,
                Goal.user_id == user_id
            ).first()
            if not task:
                return None, "任務不存在或無權限"

            task.is_completed = not task.is_completed
            task.completed_at = datetime.utcnow() if task.is_completed else None

            # 如果完成任務，重置提醒狀態
            if task.is_completed:
                task.reminder_sent = False

            db.session.commit()
            return task, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def reorder_tasks(goal_id, user_id, task_orders):
        """調整任務順序
        task_orders: [{'id': 1, 'order_index': 0}, {'id': 2, 'order_index': 1}, ...]
        """
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return False, "目標不存在或無權限"

            for item in task_orders:
                task = Task.query.filter_by(id=item['id'], goal_id=goal_id).first()
                if task:
                    task.order_index = item['order_index']

            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_upcoming_tasks(user_id, days=7):
        """獲取即將到期的任務"""
        try:
            today = date.today()
            future_date = today + timedelta(days=days)

            tasks = Task.query.join(Goal).filter(
                Goal.user_id == user_id,
                Task.is_completed == False,
                Task.due_date.between(today, future_date)
            ).order_by(Task.due_date.asc()).all()

            return tasks, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_overdue_tasks(user_id):
        """獲取逾期任務"""
        try:
            today = date.today()

            tasks = Task.query.join(Goal).filter(
                Goal.user_id == user_id,
                Task.is_completed == False,
                Task.due_date < today
            ).order_by(Task.due_date.asc()).all()

            return tasks, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def create_subtask(parent_task_id, user_id, data):
        """建立子任務"""
        try:
            # 檢查父任務是否存在且屬於該使用者
            parent_task = Task.query.join(Goal).filter(
                Task.id == parent_task_id,
                Goal.user_id == user_id
            ).first()
            if not parent_task:
                return None, "父任務不存在或無權限"

            # 防止多層巢狀（子任務的子任務）
            if parent_task.parent_task_id is not None:
                return None, "不允許建立子任務的子任務"

            # 建立子任務
            data['parent_task_id'] = parent_task_id
            return TaskService.create_task(parent_task.goal_id, user_id, data)
        except Exception as e:
            return None, str(e)
