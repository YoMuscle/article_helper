from datetime import datetime, date, timedelta
from models import db, Task, Goal, User
from services.email_service import mail
from flask_mail import Message
from flask import render_template
import os


class TaskReminderService:
    """任務提醒服務層"""

    @staticmethod
    def send_due_reminders():
        """發送到期提醒（建議使用 cron job 或 scheduler 每日執行）"""
        try:
            today = date.today()
            reminder_dates = [
                today + timedelta(days=3),  # 3天後到期
                today + timedelta(days=1),  # 1天後到期
                today                        # 今天到期
            ]

            results = {
                'sent': 0,
                'errors': 0,
                'skipped': 0
            }

            # 查詢即將到期且未發送提醒的任務
            for reminder_date in reminder_dates:
                tasks = Task.query.join(Goal).join(User).filter(
                    Task.is_completed == False,
                    Task.reminder_sent == False,
                    Task.due_date == reminder_date,
                    User.is_verified == True
                ).all()

                for task in tasks:
                    success = TaskReminderService.send_task_reminder_email(task)
                    if success:
                        task.reminder_sent = True
                        results['sent'] += 1
                    else:
                        results['errors'] += 1

            db.session.commit()
            return results
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}

    @staticmethod
    def send_task_reminder_email(task):
        """發送單一任務提醒 email"""
        try:
            # 檢查 mail 服務是否已配置
            if not mail or not os.getenv('MAIL_USERNAME'):
                print(f"[REMINDER] Email service not configured, skipping reminder for task: {task.title}")
                return False

            user = task.goal.user
            days_until_due = (task.due_date - date.today()).days

            # 決定提醒標題
            if days_until_due == 0:
                subject = f"📌 任務今天到期：{task.title}"
                urgency = "今天"
            elif days_until_due == 1:
                subject = f"⏰ 任務明天到期：{task.title}"
                urgency = "明天"
            elif days_until_due == 3:
                subject = f"📅 任務3天後到期：{task.title}"
                urgency = "3天後"
            else:
                subject = f"📋 任務即將到期：{task.title}"
                urgency = f"{days_until_due}天後"

            # 建立 email 內容
            app_url = os.getenv('APP_URL', 'http://localhost:5000')
            goal_url = f"{app_url}/my-goals/{task.goal_id}"

            msg = Message(
                subject=subject,
                recipients=[user.email],
                html=render_template(
                    'emails/task_reminder.html',
                    user=user,
                    task=task,
                    goal=task.goal,
                    urgency=urgency,
                    days_until_due=days_until_due,
                    goal_url=goal_url
                )
            )

            mail.send(msg)
            print(f"[REMINDER] Sent reminder to {user.email} for task: {task.title}")
            return True
        except Exception as e:
            print(f"[REMINDER ERROR] Failed to send reminder: {str(e)}")
            return False

    @staticmethod
    def reset_reminders_for_task(task_id):
        """重置任務的提醒狀態（當任務日期變更時）"""
        try:
            task = Task.query.get(task_id)
            if task:
                task.reminder_sent = False
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            return False
