from flask import Blueprint, jsonify
from app import db
from models import Project, Task
from datetime import date

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/overview', methods=['GET'])
def get_overview():
    """获取所有项目的概览统计"""
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    total = len(projects)
    active = Project.query.filter_by(status='active').count()
    completed = Project.query.filter_by(status='completed').count()

    overdue_projects = 0
    total_overdue_tasks = 0
    today = date.today()

    for p in projects:
        overdue = Task.query.filter(
            Task.project_id == p.id,
            Task.status != 'completed',
            Task.deadline < today
        ).count()
        if overdue > 0:
            overdue_projects += 1
        total_overdue_tasks += overdue

    return jsonify({
        'total_projects': total,
        'active_projects': active,
        'completed_projects': completed,
        'overdue_projects': overdue_projects,
        'total_overdue_tasks': total_overdue_tasks,
    })
