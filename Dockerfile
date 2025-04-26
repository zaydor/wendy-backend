# Use official lightweight Python image
FROM python:3.13.3-slim-bullseye

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create virtual environment and install dependencies
RUN uv venv && uv pip install -r requirements.txt

# Command to run the app
CMD .venv/bin/gunicorn --bind 0.0.0.0:5050 app:app
