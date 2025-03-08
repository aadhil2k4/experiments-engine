#!/bin/bash
python -m alembic upgrade head

# Run background cron job for `create_notifications.py` to run every 5 minutes
(crontab -l 2>/dev/null; \
  echo "*/5 * * * * $(which python) $(pwd)/create_notifications.py >> /tmp/create_notifications.log 2>&1") | crontab

exec gunicorn -k main.Worker -w 4 -b 0.0.0.0:8000 --preload \
    -c gunicorn_hooks_config.py main:app
#
