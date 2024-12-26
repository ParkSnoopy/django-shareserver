# gunicorn.conf.py

from datetime import datetime
import os

if not os.path.exists(".logs"):
    os.makedirs(".logs")
    os.makedirs(".logs/gunicorn")

bind    = "127.0.0.1:8200"
reload  = True

workers = 1
# worker_class = "uvicorn.workers.UvicornWorker"

# accesslog = "-"
# errorlog  = "-"
accesslog = f"./.logs/gunicorn/access_{datetime.now().strftime('%Y-%m-%d_%H')}.log"
errorlog  = f"./.logs/gunicorn/error_{datetime.now().strftime('%Y-%m-%d_%H')}.log"
loglevel  = "info"

wsgi_app  = "compactSharing.wsgi:application"
