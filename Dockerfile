FROM python:3.10-slim-buster

WORKDIR /app
COPY . /app

# Update package lists and install AWS CLI
RUN apt-get update -y && apt-get install -y awscli

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the application
CMD ["python3", "app.py"]
