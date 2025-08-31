# Web process
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 --worker-class gevent --worker-connections 1000 --log-level=info --access-logfile - --error-logfile - wsgi:application

# Worker process for background tasks
worker: celery -A app.celery worker --loglevel=info

# Beat process for scheduled tasks
beat: celery -A app.celery beat --loglevel=info

# Database migrations (run once on deploy)
release: python manage.py db upgrade

# Command to run before the application starts
predeploy: python manage.py db upgrade && python manage.py collectstatic --no-input
