from app import db
from datetime import datetime, date
from sqlalchemy import func

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='active')  # active / paused / completed / cancelled
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship('Task', backref='project', lazy='dynamic',
                            cascade='all, delete-orphan')

    def to_dict(self, include_tasks=False):
        # 计算总进度
        task_count = Task.query.filter_by(project_id=self.id).count()
        if task_count > 0:
            total_progress = db.session.query(func.sum(Task.progress)).filter(
                Task.project_id == self.id
            ).scalar() or 0
            avg_progress = round(total_progress / task_count, 1)
        else:
            avg_progress = 0.0

        # 计算逾期任务数（仅统计未完成且截止日期已过的任务）
        overdue = Task.query.filter(
            Task.project_id == self.id,
            Task.status != 'completed',
            Task.deadline < date.today()
        ).count()

        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'progress': avg_progress,
            'task_count': task_count,
            'overdue_count': overdue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_tasks:
            tasks_q = Task.query.filter_by(project_id=self.id).order_by(Task.sort_order, Task.id).all()
            result['tasks'] = [t.to_dict() for t in tasks_q]

        return result


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, default='')
    assignee = db.Column(db.String(100), default='')  # 负责人名字
    status = db.Column(db.String(20), default='todo')  # todo / in_progress / completed / cancelled
    priority = db.Column(db.Integer, default=2)  # 0=P0最高, 1=P1, 2=P2, 3=P3
    progress = db.Column(db.Integer, default=0)  # 0-100
    start_date = db.Column(db.Date, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    remark = db.Column(db.Text, default='')  # 每日备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 自引用关系
    children = db.relationship(
        'Task', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic', cascade='all, delete-orphan'
    )

    def to_dict(self):
        # 如果有关联子任务，进度从子任务汇总
        child_count = self.children.count()
        if child_count > 0:
            total_progress = db.session.query(func.sum(Task.progress)).filter(
                Task.parent_id == self.id
            ).scalar() or 0
            computed_progress = round(total_progress / child_count, 1)
        else:
            computed_progress = self.progress

        return {
            'id': self.id,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'title': self.title,
            'description': self.description,
            'assignee': self.assignee,
            'status': self.status,
            'priority': self.priority,
            'progress': computed_progress,
            'raw_progress': self.progress,  # 手动填的值
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'sort_order': self.sort_order,
            'remark': self.remark,
            'child_count': child_count,
            'is_overdue': (
                self.deadline is not None
                and self.status != 'completed'
                and self.deadline < date.today()
            ),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
