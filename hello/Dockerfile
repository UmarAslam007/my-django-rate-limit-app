# Use official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default command (you can override in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
