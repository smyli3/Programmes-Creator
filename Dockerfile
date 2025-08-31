# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (if using Flask-Collect)
RUN if [ -f "manage.py" ]; then python manage.py collectstatic --noinput; fi

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads

# Set the default command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]

# Expose the port the app runs on
EXPOSE 5000
