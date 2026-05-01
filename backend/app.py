from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import timedelta
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER', 'pm_user')}:{os.getenv('DB_PASS', 'pm_pass_2026')}"
        f"@{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'project_manager')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False  # 支持中文

    CORS(app)
    db.init_app(app)

    # 注册蓝图
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.stats import stats_bp

    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    # 健康检查
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'service': 'project-manager'}

    # 创建表
    with app.app_context():
        from models import Project, Task
        db.create_all()
        print('[DB] 表结构创建完成')

    return app

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
