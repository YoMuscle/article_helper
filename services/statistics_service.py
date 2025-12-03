from datetime import datetime, date, timedelta
from models import db, Goal, Task, GoalStatistics, User
from sqlalchemy import func


class StatisticsService:
    """統計服務層"""

    @staticmethod
    def generate_daily_snapshot(user_id):
        """產生每日統計快照"""
        try:
            today = date.today()

            # 檢查今天是否已有快照
            existing = GoalStatistics.query.filter_by(
                user_id=user_id,
                date=today
            ).first()

            if existing:
                # 更新現有快照
                snapshot = existing
            else:
                # 建立新快照
                snapshot = GoalStatistics(user_id=user_id, date=today)
                db.session.add(snapshot)

            # 計算統計數據
            goals = Goal.query.filter_by(user_id=user_id).all()
            snapshot.total_goals = len(goals)
            snapshot.active_goals = sum(1 for g in goals if g.status == 'active')
            snapshot.completed_goals = sum(1 for g in goals if g.status == 'completed')
            snapshot.archived_goals = sum(1 for g in goals if g.status == 'archived')

            # 計算任務統計
            tasks = Task.query.join(Goal).filter(Goal.user_id == user_id).all()
            snapshot.total_tasks = len(tasks)
            snapshot.completed_tasks = sum(1 for t in tasks if t.is_completed)
            snapshot.completion_rate = round(
                (snapshot.completed_tasks / snapshot.total_tasks * 100) if snapshot.total_tasks > 0 else 0,
                1
            )

            db.session.commit()
            return snapshot, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_dashboard_data(user_id):
        """獲取儀表板數據"""
        try:
            # 基本統計
            goals = Goal.query.filter_by(user_id=user_id).all()
            total_goals = len(goals)
            active_goals = sum(1 for g in goals if g.status == 'active')
            completed_goals = sum(1 for g in goals if g.status == 'completed')

            tasks = Task.query.join(Goal).filter(Goal.user_id == user_id).all()
            total_tasks = len(tasks)
            completed_tasks = sum(1 for t in tasks if t.is_completed)

            overall_completion_rate = round(
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                1
            )

            # 本週到期任務
            today = date.today()
            week_end = today + timedelta(days=7)
            tasks_due_this_week = Task.query.join(Goal).filter(
                Goal.user_id == user_id,
                Task.is_completed == False,
                Task.due_date.between(today, week_end)
            ).count()

            # 逾期任務
            overdue_tasks = Task.query.join(Goal).filter(
                Goal.user_id == user_id,
                Task.is_completed == False,
                Task.due_date < today
            ).count()

            # 最近活動（最近完成的5個任務）
            recent_completed = Task.query.join(Goal).filter(
                Goal.user_id == user_id,
                Task.is_completed == True
            ).order_by(Task.completed_at.desc()).limit(5).all()

            recent_activity = []
            for task in recent_completed:
                recent_activity.append({
                    'type': 'task_completed',
                    'task_title': task.title,
                    'goal_title': task.goal.title,
                    'timestamp': task.completed_at.isoformat() if task.completed_at else None
                })

            # 生產力趨勢（過去30天）
            productivity_trend = StatisticsService.get_productivity_trend(user_id, days=30)

            return {
                'summary': {
                    'total_goals': total_goals,
                    'active_goals': active_goals,
                    'completed_goals': completed_goals,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'overall_completion_rate': overall_completion_rate,
                    'tasks_due_this_week': tasks_due_this_week,
                    'overdue_tasks': overdue_tasks
                },
                'recent_activity': recent_activity,
                'productivity_trend': productivity_trend
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_productivity_trend(user_id, days=30):
        """獲取生產力趨勢數據"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days - 1)

            # 獲取歷史統計數據
            stats = GoalStatistics.query.filter(
                GoalStatistics.user_id == user_id,
                GoalStatistics.date.between(start_date, end_date)
            ).order_by(GoalStatistics.date.asc()).all()

            # 如果統計數據不完整，補充當天數據
            existing_dates = {stat.date for stat in stats}
            current_date = start_date
            while current_date <= end_date:
                if current_date not in existing_dates:
                    # 計算該日的統計（簡化版，實際應該根據歷史數據）
                    snapshot, _ = StatisticsService.generate_daily_snapshot(user_id)
                    if snapshot:
                        stats.append(snapshot)
                current_date += timedelta(days=1)

            # 重新排序
            stats.sort(key=lambda x: x.date)

            trend_data = []
            for stat in stats:
                trend_data.append({
                    'date': stat.date.isoformat(),
                    'completion_rate': stat.completion_rate
                })

            return trend_data
        except Exception as e:
            return []

    @staticmethod
    def calculate_completion_rate(user_id):
        """計算整體完成率"""
        try:
            tasks = Task.query.join(Goal).filter(Goal.user_id == user_id).all()
            total_tasks = len(tasks)
            if total_tasks == 0:
                return 0

            completed_tasks = sum(1 for t in tasks if t.is_completed)
            return round((completed_tasks / total_tasks * 100), 1)
        except Exception as e:
            return 0

    @staticmethod
    def get_priority_distribution(user_id):
        """獲取優先級分布"""
        try:
            tasks = Task.query.join(Goal).filter(
                Goal.user_id == user_id,
                Task.is_completed == False
            ).all()

            distribution = {
                'high': 0,
                'medium': 0,
                'low': 0
            }

            for task in tasks:
                if task.priority in distribution:
                    distribution[task.priority] += 1

            return distribution, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def generate_daily_snapshot_for_all():
        """為所有使用者產生每日統計快照（由排程器調用）"""
        try:
            users = User.query.filter_by(is_verified=True).all()
            success_count = 0
            error_count = 0

            for user in users:
                snapshot, error = StatisticsService.generate_daily_snapshot(user.id)
                if error:
                    error_count += 1
                else:
                    success_count += 1

            return {
                'success': success_count,
                'errors': error_count
            }
        except Exception as e:
            return {'error': str(e)}
