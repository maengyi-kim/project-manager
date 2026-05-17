#!/usr/bin/env python3.11
"""启动项目管家后端服务"""

import subprocess, sys, os, time

# 使用用户目录存储日志
log_dir = os.path.expanduser("~/logs")
os.makedirs(log_dir, exist_ok=True)

os.chdir("/home/kk/ai_project/project_manager/backend")

# 使用虚拟环境中的gunicorn
cmd = [
    "./venv/bin/gunicorn",
    "-w",
    "2",
    "-b",
    "0.0.0.0:5001",
    "--timeout",
    "120",
    "--access-logfile",
    f"{log_dir}/pm_access.log",
    "--error-logfile",
    f"{log_dir}/pm_error.log",
    "app:create_app()",
]

proc = subprocess.Popen(
    cmd,
    stdout=open(f"{log_dir}/pm_app.log", "a"),
    stderr=subprocess.STDOUT,
)

print(f"PID: {proc.pid}")
sys.exit(0)
