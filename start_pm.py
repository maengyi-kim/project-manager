#!/usr/bin/env python3.11
"""启动项目管家后端服务"""
import subprocess, sys, os, time

os.chdir('/data/project_manager/backend')

cmd = [
    'gunicorn',
    '-w', '2',
    '-b', '0.0.0.0:5001',
    '--timeout', '120',
    '--access-logfile', '/var/log/pm_access.log',
    '--error-logfile', '/var/log/pm_error.log',
    'app:create_app()',
]

proc = subprocess.Popen(
    cmd,
    stdout=open('/var/log/pm_app.log', 'a'),
    stderr=subprocess.STDOUT,
)

print(f'PID: {proc.pid}')
sys.exit(0)
