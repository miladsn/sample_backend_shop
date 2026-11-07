# Python 3.12 Slim production base
FROM python:3.12-slim

# Using the Slim version of Python for Linux
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Prevent logs from buffering and creating pyc files
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copying and Installing Libraries
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Django code
COPY . /app/

# Default Port
EXPOSE 8000

# Do not run Django until MySQL is truly ready.
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

# Django Execution Command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
