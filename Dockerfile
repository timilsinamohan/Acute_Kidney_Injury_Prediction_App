# Use a lightweight Python base image
FROM python:3.9-slim

# Create a working directory
WORKDIR /app

# Set environment variables to reduce pip concurrency issues
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_PROGRESS_BAR=off \
    PIP_MAX_PARALLEL=1 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    FLASK_DEBUG=0 \
    NUMEXPR_NUM_THREADS=1

# Copy requirements.txt first
COPY requirements.txt .

# Install dependencies (without upgrading pip)
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application files
COPY . .

# Expose port 5001
EXPOSE 5001

# Default command to run your app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]