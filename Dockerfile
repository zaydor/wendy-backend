# Use official lightweight Python image
FROM python:3.13.3-slim-bullseye

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 5050

# Command to run the app
CMD ["python", "app.py"]
