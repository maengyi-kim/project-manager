from flask import Blueprint, request, jsonify
from app import db
from models import Task, Project
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['GET'])
def list_tasks():
    """获取项目下的所有任务（或指定父任务下的子任务）"""
    project_id = request.args.get('project_id', type=int)
    parent_id = request.args.get('parent_id', type=int)

    query = Task.query

    if project_id:
        query = query.filter_by(project_id=project_id)
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    else:
        query = query.filter_by(parent_id=None)  # 只查顶层任务

    tasks = query.order_by(Task.sort_order, Task.id).all()
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.route('/tree/<int:project_id>', methods=['GET'])
def get_task_tree(project_id):
    """获取项目的完整任务树（平铺列表+层级信息，适合小程序端渲染）"""
    project = Project.query.get_or_404(project_id)
    all_tasks = Task.query.filter_by(project_id=project_id).order_by(Task.sort_order, Task.id).all()

    result = []
    for t in all_tasks:
        d = t.to_dict()
        result.append(d)

    return jsonify(result)


@tasks_bp.route('/gantt/<int:project_id>', methods=['GET'])
def get_gantt_data(project_id):
    """获取甘特图数据（只取有起止日期的任务，含层级关系）"""
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter(
        Task.project_id == project_id,
        Task.start_date.isnot(None),
        Task.deadline.isnot(None)
    ).order_by(Task.sort_order, Task.id).all()

    items = []
    for t in tasks:
        d = t.to_dict()
        items.append({
            'id': d['id'],
            'parent_id': d['parent_id'],
            'title': d['title'],
            'start_date': d['start_date'],
            'deadline': d['deadline'],
            'progress': d['progress'],
            'status': d['status'],
            'sort_order': d['sort_order'],
            'assignee': d['assignee'],
            'depth': _calc_depth(t),
        })

    return jsonify({
        'project': {'id': project.id, 'name': project.name, 'start_date': project.start_date.isoformat() if project.start_date else None, 'end_date': project.end_date.isoformat() if project.end_date else None},
        'tasks': items,
    })


def _calc_depth(task, depth=0):
    if task.parent_id is None:
        return depth
    parent = Task.query.get(task.parent_id)
    if parent:
        return _calc_depth(parent, depth + 1)
    return depth


@tasks_bp.route('', methods=['POST'])
def create_task():
    """创建任务"""
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': '任务名称不能为空'}), 400

    project = Project.query.get_or_404(data['project_id'])

    # 新任务默认排到最后
    max_sort = db.session.query(db.func.max(Task.sort_order)).filter(
        Task.project_id == data['project_id']
    ).scalar() or 0

    task = Task(
        project_id=data['project_id'],
        parent_id=data.get('parent_id'),  # None 则为顶层任务
        title=data['title'],
        description=data.get('description', ''),
        assignee=data.get('assignee', ''),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 2),
        progress=data.get('progress', 0),
        sort_order=data.get('sort_order', max_sort + 1),
        remark=data.get('remark', ''),
    )

    if data.get('start_date'):
        task.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if data.get('deadline'):
        task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()

    db.session.add(task)

    # 如果有关联的子任务更新，递归更新父任务进度
    _update_parent_progress(task.parent_id)

    return jsonify(task.to_dict()), 201


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'assignee' in data:
        task.assignee = data['assignee']
    if 'status' in data:
        task.status = data['status']
        if data['status'] == 'completed':
            task.progress = 100
        elif data['status'] == 'todo':
            task.progress = 0
    if 'priority' in data:
        task.priority = data['priority']
    if 'progress' in data:
        task.progress = data['progress']
        # 如果是叶子任务（无子任务）且进度为100%，自动设置状态为completed
        if task.children.count() == 0 and task.progress == 100:
            task.status = 'completed'
    if 'remark' in data:
        task.remark = data['remark']
    if 'sort_order' in data:
        task.sort_order = data['sort_order']
    if 'start_date' in data:
        task.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data['start_date'] else None
    if 'deadline' in data:
        task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data['deadline'] else None


    # 递归更新父任务进度
    _update_parent_progress(task.parent_id)

    return jsonify(task.to_dict())


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    task = Task.query.get_or_404(task_id)
    parent_id = task.parent_id
    db.session.delete(task)

    if parent_id:
        _update_parent_progress(parent_id)

    return jsonify({'message': '任务已删除'})


def _update_parent_progress(parent_id):
    """递归更新父任务进度（基于子任务平均值）"""
    if parent_id is None:
        return

    parent = Task.query.get(parent_id)
    if parent is None:
        return

    children = Task.query.filter_by(parent_id=parent_id).all()
    if children:
        parent.progress = round(sum(c.progress for c in children) / len(children), 1)
        # 如果所有子任务都完成了，父任务也标记为完成
        if parent.progress == 100:
            parent.status = 'completed'

    _update_parent_progress(parent.parent_id)
