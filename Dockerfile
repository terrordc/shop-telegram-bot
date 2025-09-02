# Start with the same OS as your VPS
FROM ubuntu:22.04

# Set environment variables to prevent interactive prompts during setup
ENV DEBIAN_FRONTEND=noninteractive
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VERSION=1.8.2

# Install system dependencies, including the Python version you need
RUN apt-get update && \
    apt-get install -y --no-install-recommendations \
    python3.10 \
    python3.10-dev \
    python3.10-venv \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory inside the container
WORKDIR /app

# Copy your project files into the container
COPY . .

# Install your project's Python libraries
RUN $POETRY_HOME/bin/poetry install --no-root

# The command to run when the container starts
CMD ["/opt/poetry/bin/poetry", "run", "python", "src/__init__.py"]