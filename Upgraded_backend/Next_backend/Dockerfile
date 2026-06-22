FROM python:3.10-slim

# Root working dir
WORKDIR /app

# System packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Env vars
ENV PIP_NO_CACHE_DIR=1
ENV PIP_TIMEOUT=120
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CHROMA_DB_PATH=/tmp/chroma_db
ENV HF_HOME=/tmp/hf
ENV TRANSFORMERS_CACHE=/tmp/hf
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/hf

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Go inside backend folder
WORKDIR /app/Next_backend

# HF Spaces port
EXPOSE 7860

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]