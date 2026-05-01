from flask import Blueprint, request, jsonify
from app import db
from models import Project, Task
from datetime import datetime

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('', methods=['GET'])
def list_projects():
    """获取所有项目列表"""
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return jsonify([p.to_dict() for p in projects])


@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取单个项目详情（含任务树）"""
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict(include_tasks=True))


@projects_bp.route('', methods=['POST'])
def create_project():
    """创建项目"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': '项目名称不能为空'}), 400

    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        status=data.get('status', 'active'),
    )

    # 解析日期
    if data.get('start_date'):
        project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if data.get('end_date'):
        project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']
    if 'start_date' in data:
        project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data['start_date'] else None
    if 'end_date' in data:
        project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None

    db.session.commit()
    return jsonify(project.to_dict())


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': '项目已删除'})


@projects_bp.route('/<int:project_id>/share', methods=['GET'])
def share_project(project_id):
    """获取项目分享数据（只看模式，不含编辑信息）"""
    project = Project.query.get_or_404(project_id)
    data = project.to_dict(include_tasks=True)
    # 去掉内部字段
    for task in data.get('tasks', []):
        for key in ['created_at', 'updated_at', 'raw_progress']:
            task.pop(key, None)
    return jsonify(data)
