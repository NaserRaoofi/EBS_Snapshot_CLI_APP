# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install build tools
RUN pip install --upgrade pip && pip install build

# Copy source code
COPY . .

# Build the wheel inside the container
RUN python -m build

# Install the built wheel
RUN pip install --no-cache-dir dist/*.whl

# (Optional) Set entrypoint or CMD
# CMD ["python", "cli.py"]
