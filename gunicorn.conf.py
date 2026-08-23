"""Gunicorn config for VPS deployment (e.g. behind Nginx)."""
bind = "127.0.0.1:8000"
workers = 3               # rule of thumb: (2 x CPU cores) + 1
worker_class = "sync"
timeout = 30
accesslog = "-"
errorlog = "-"
loglevel = "info"
