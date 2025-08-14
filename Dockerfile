FROM python:3.9-slim

# Install system dependencies for GUI applications
RUN apt-get update && apt-get install -y \\
    python3-tk \\
    libpng-dev \\
    libjpeg-dev \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false && \\
    poetry install --no-dev

# Copy application files
COPY main.py ./
COPY data/ ./data/

# Set environment variables for GUI
ENV DISPLAY=:0

# Expose port (if needed for future web version)
EXPOSE 8050

# Run the application
CMD ["python", "main.py"]