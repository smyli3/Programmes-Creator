web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 --log-level=info --access-logfile - --error-logfile - wsgi:application

# Run database migrations on each deploy
release: FLASK_APP=wsgi.py flask db upgrade
