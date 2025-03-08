# Use an official Python runtime as a base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure that Python output is logged straight to the terminal (e.g., for Docker logs)
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd gcc libpq-dev


# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project code into the container
COPY . .

# Expose the port Django will run on (default is 8000)
EXPOSE 8000

# Start the Django development server
# CMD ["python3", "myproject/manage.py", "runserver", "0.0.0.0:8000"]
CMD ["python3", "myproject/manage.py", "runserver", "0.0.0.0:8000"] 

