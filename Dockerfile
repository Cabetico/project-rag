# FROM python:3.12-slim

# # Install system dependencies (curl + bash + build tools if needed)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     bash \
#     && rm -rf /var/lib/apt/lists/*

# RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# # Install uv
# RUN pip install --no-cache-dir uv

# # Set workdir
# WORKDIR /app

# # Copy dependency files first (for caching)
# COPY pyproject.toml uv.lock ./

# # Install dependencies in a virtualenv inside container
# RUN uv sync --frozen --no-dev

# # Copy your app code
# COPY frontend/ ./frontend/
# COPY e_commerce_rag ./e_commerce_rag

# # Copy entryopoint script
# COPY entrypoint.sh /app/entrypoint.sh
# COPY init-entrypoint.sh /app/init-entrypoint.sh
# #RUN chmod +x /app/entrypoiny.sh

# # Expose port
# EXPOSE 8000
# EXPOSE 8501

# # Start with Gunicorn using uv’s venv
# ENTRYPOINT ["/app/entrypoint.sh"]
# #CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "e_commerce_rag.app:app"]


FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bash postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files and install
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy your app code
COPY frontend/ ./frontend/
COPY e_commerce_rag ./e_commerce_rag

# Copy entrypoint scripts
COPY entrypoint.sh /app/entrypoint.sh


# Make scripts executable
RUN chmod +x /app/entrypoint.sh 

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Default entrypoint (python-app)
ENTRYPOINT ["/app/entrypoint.sh"]