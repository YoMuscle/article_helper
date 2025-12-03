from flask import Blueprint, request, jsonify
from flask_login import current_user
from utils.decorators import login_required, verified_required
from services.goal_service import GoalService
from services.task_service import TaskService
from services.statistics_service import StatisticsService
from models import db, TaskTag, Goal, Task

bp = Blueprint('goals', __name__, url_prefix='/api')


# ==================== 目標管理 API ====================

@bp.route('/goals', methods=['GET'])
@verified_required
def get_goals():
    """獲取使用者所有目標"""
    try:
        status = request.args.get('status')  # 可選：active, completed, archived
        goals, error = GoalService.get_user_goals(current_user.id, status)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({
            "goals": [goal.to_dict() for goal in goals]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals', methods=['POST'])
@verified_required
def create_goal():
    """新增目標"""
    try:
        data = request.get_json()

        # 驗證必填欄位
        if not data.get('title'):
            return jsonify({"error": "目標標題為必填"}), 400

        goal, error = GoalService.create_goal(current_user.id, data)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({
            "message": "目標建立成功",
            "goal": goal.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals/<int:goal_id>', methods=['GET'])
@verified_required
def get_goal(goal_id):
    """獲取特定目標詳情"""
    try:
        goal, error = GoalService.get_goal_by_id(goal_id, current_user.id)

        if error:
            return jsonify({"error": error}), 404

        # 包含任務列表
        tasks = Task.query.filter_by(
            goal_id=goal_id,
            parent_task_id=None  # 只取主任務，子任務會在主任務的 to_dict 中包含
        ).order_by(Task.order_index.asc()).all()

        goal_data = goal.to_dict()
        goal_data['tasks'] = [task.to_dict(include_subtasks=True) for task in tasks]

        return jsonify({"goal": goal_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals/<int:goal_id>', methods=['PUT'])
@verified_required
def update_goal(goal_id):
    """更新目標"""
    try:
        data = request.get_json()
        goal, error = GoalService.update_goal(goal_id, current_user.id, data)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({
            "message": "目標更新成功",
            "goal": goal.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals/<int:goal_id>', methods=['DELETE'])
@verified_required
def delete_goal(goal_id):
    """刪除目標"""
    try:
        success, error = GoalService.delete_goal(goal_id, current_user.id)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({"message": "目標刪除成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals/<int:goal_id>/status', methods=['PUT'])
@verified_required
def update_goal_status(goal_id):
    """更新目標狀態"""
    try:
        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['active', 'completed', 'archived']:
            return jsonify({"error": "無效的狀態值"}), 400

        goal, error = GoalService.update_goal_status(goal_id, current_user.id, new_status)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({
            "message": "狀態更新成功",
            "goal": goal.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 任務管理 API ====================

@bp.route('/goals/<int:goal_id>/tasks', methods=['GET'])
@verified_required
def get_goal_tasks(goal_id):
    """獲取目標下的所有任務"""
    try:
        # 驗證目標存在且屬於該使用者
        goal, error = GoalService.get_goal_by_id(goal_id, current_user.id)
        if error:
            return jsonify({"error": error}), 404

        # 只獲取主任務（子任務會在主任務的 to_dict 中包含）
        tasks = Task.query.filter_by(
            goal_id=goal_id,
            parent_task_id=None
        ).order_by(Task.order_index.asc()).all()

        return jsonify({
            "tasks": [task.to_dict(include_subtasks=True) for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals/<int:goal_id>/tasks', methods=['POST'])
@verified_required
def create_task(goal_id):
    """在目標下新增任務"""
    try:
        data = request.get_json()

        # 驗證必填欄位
        if not data.get('title'):
            return jsonify({"error": "任務標題為必填"}), 400

        task, error = TaskService.create_task(goal_id, current_user.id, data)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({
            "message": "任務建立成功",
            "task": task.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tasks/<int:task_id>', methods=['GET'])
@verified_required
def get_task(task_id):
    """獲取任務詳情"""
    try:
        task = Task.query.join(Goal).filter(
            Task.id == task_id,
            Goal.user_id == current_user.id
        ).first()

        if not task:
            return jsonify({"error": "任務不存在或無權限存取"}), 404

        return jsonify({"task": task.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tasks/<int:task_id>', methods=['PUT'])
@verified_required
def update_task(task_id):
    """更新任務"""
    try:
        data = request.get_json()
        task, error = TaskService.update_task(task_id, current_user.id, data)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({
            "message": "任務更新成功",
            "task": task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@verified_required
def delete_task(task_id):
    """刪除任務"""
    try:
        success, error = TaskService.delete_task(task_id, current_user.id)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({"message": "任務刪除成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tasks/<int:task_id>/complete', methods=['PUT'])
@verified_required
def toggle_task_completion(task_id):
    """切換任務完成狀態"""
    try:
        task, error = TaskService.toggle_task_completion(task_id, current_user.id)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({
            "message": "任務狀態更新成功",
            "task": task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals/<int:goal_id>/tasks/reorder', methods=['PUT'])
@verified_required
def reorder_tasks(goal_id):
    """調整任務順序"""
    try:
        data = request.get_json()
        task_orders = data.get('task_orders', [])

        success, error = TaskService.reorder_tasks(goal_id, current_user.id, task_orders)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 500

        return jsonify({"message": "任務順序更新成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 子任務管理 API ====================

@bp.route('/tasks/<int:task_id>/subtasks', methods=['GET'])
@verified_required
def get_subtasks(task_id):
    """獲取子任務列表"""
    try:
        # 驗證父任務存在且屬於該使用者
        parent_task = Task.query.join(Goal).filter(
            Task.id == task_id,
            Goal.user_id == current_user.id
        ).first()

        if not parent_task:
            return jsonify({"error": "任務不存在或無權限存取"}), 404

        return jsonify({
            "subtasks": [st.to_dict(include_subtasks=False) for st in parent_task.subtasks]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tasks/<int:task_id>/subtasks', methods=['POST'])
@verified_required
def create_subtask(task_id):
    """新增子任務"""
    try:
        data = request.get_json()

        # 驗證必填欄位
        if not data.get('title'):
            return jsonify({"error": "子任務標題為必填"}), 400

        subtask, error = TaskService.create_subtask(task_id, current_user.id, data)

        if error:
            return jsonify({"error": error}), 404 if "不存在" in error else 400

        return jsonify({
            "message": "子任務建立成功",
            "subtask": subtask.to_dict(include_subtasks=False)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 標籤管理 API ====================

@bp.route('/tags', methods=['GET'])
@verified_required
def get_tags():
    """獲取使用者所有標籤"""
    try:
        tags = TaskTag.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            "tags": [tag.to_dict() for tag in tags]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tags', methods=['POST'])
@verified_required
def create_tag():
    """新增標籤"""
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({"error": "標籤名稱為必填"}), 400

        # 檢查標籤是否已存在
        existing = TaskTag.query.filter_by(
            user_id=current_user.id,
            name=data['name']
        ).first()

        if existing:
            return jsonify({"error": "標籤名稱已存在"}), 400

        tag = TaskTag(
            user_id=current_user.id,
            name=data['name'],
            color=data.get('color', 'secondary')
        )
        db.session.add(tag)
        db.session.commit()

        return jsonify({
            "message": "標籤建立成功",
            "tag": tag.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route('/tags/<int:tag_id>', methods=['PUT'])
@verified_required
def update_tag(tag_id):
    """更新標籤"""
    try:
        tag = TaskTag.query.filter_by(id=tag_id, user_id=current_user.id).first()
        if not tag:
            return jsonify({"error": "標籤不存在或無權限更新"}), 404

        data = request.get_json()
        if 'name' in data:
            tag.name = data['name']
        if 'color' in data:
            tag.color = data['color']

        db.session.commit()

        return jsonify({
            "message": "標籤更新成功",
            "tag": tag.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@verified_required
def delete_tag(tag_id):
    """刪除標籤"""
    try:
        tag = TaskTag.query.filter_by(id=tag_id, user_id=current_user.id).first()
        if not tag:
            return jsonify({"error": "標籤不存在或無權限刪除"}), 404

        db.session.delete(tag)
        db.session.commit()

        return jsonify({"message": "標籤刪除成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ==================== 統計與儀表板 API ====================

@bp.route('/goals/dashboard', methods=['GET'])
@verified_required
def get_dashboard():
    """獲取儀表板統計數據"""
    try:
        data, error = StatisticsService.get_dashboard_data(current_user.id)

        if error:
            return jsonify({"error": error}), 500

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/goals/statistics', methods=['GET'])
@verified_required
def get_statistics():
    """獲取歷史統計（用於趨勢圖）"""
    try:
        days = int(request.args.get('days', 30))
        trend_data = StatisticsService.get_productivity_trend(current_user.id, days)

        return jsonify({
            "productivity_trend": trend_data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tasks/upcoming', methods=['GET'])
@verified_required
def get_upcoming_tasks():
    """獲取即將到期的任務"""
    try:
        days = int(request.args.get('days', 7))
        tasks, error = TaskService.get_upcoming_tasks(current_user.id, days)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({
            "tasks": [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/tasks/overdue', methods=['GET'])
@verified_required
def get_overdue_tasks():
    """獲取逾期任務"""
    try:
        tasks, error = TaskService.get_overdue_tasks(current_user.id)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({
            "tasks": [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
