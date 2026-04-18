# Qwen Medical Transcriber - Docker Image
# Based on NVIDIA CUDA runtime for GPU acceleration

# Use NVIDIA CUDA runtime base image
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    wget \
    curl \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Установка FFmpeg для обработки аудио
RUN apt-get update && apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY app/ ./app/
COPY win32/gui/ ./win32/gui/ 2>/dev/null || true

# Создание директорий для данных
RUN mkdir -p /app/models /app/uploads /app/output /app/logs

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/models
ENV TRANSFORMERS_CACHE=/app/models
ENV TORCH_HOME=/app/models
ENV HF_HUB_OFFLINE=1
ENV HF_OFFLINE=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Порт для Gradio Web UI
EXPOSE 7860

# Запуск Gradio Web UI
CMD ["/opt/venv/bin/python", "-m", "gradio", "app/main.py"]
