""" Settings file for gunicorn configuration
 How to use it from command line: gunicorn apilog.wsgi:application -c settings.py
"""
import multiprocessing

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
loglevel = 'debug'
backlog = 2048
errorlog = '/opt/bvp/log/gunicorn-error.log'
accesslog = '/opt/bvp/log/gunicorn-access.log'