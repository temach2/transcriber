# Установка моделей Qwen Medical Transcriber

**Инструкция по установке локальных моделей**

---

## 📦 Требуемые модели

Для работы системы необходимы три модели:

| Модель | Описание | Размер | Путь |
|--------|----------|--------|------|
| Qwen3-ASR-1.7B | Распознавание речи | ~3.4 GB | `./models/Qwen3-ASR-1.7B/` |
| Qwen3-ForcedAligner-0.6B | Выравнивание таймкодов | ~1.2 GB | `./models/Qwen3-ForcedAligner-0.6B/` |
| pyannote-speaker-diarization-3.1 | Диаризация спикеров | ~250 MB | `./models/pyannote-speaker-diarization-3.1/` |

**Общий размер:** ~4.9 GB

---

## 🚀 Способ 1: Автоматическая загрузка (требует интернет)

### Шаг 1: Установка зависимостей

```bash
# Linux/Mac
pip install -r requirements.txt

# Windows
pip install -r requirements-win32.txt
```

### Шаг 2: Запуск скрипта загрузки

```python
# download_models.py
import os
from huggingface_hub import snapshot_download

# Установка OFLINE режима (после загрузки)
os.environ['HF_HUB_OFFLINE'] = '1'

# Загрузка моделей
def download_model(model_id, local_dir):
    print(f"Загрузка {model_id}...")
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        resume_download=True
    )
    print(f"Модель {model_id} загружена в {local_dir}")

# Загрузка
download_model(
    "Qwen/Qwen3-ASR-1.7B",
    "./models/Qwen3-ASR-1.7B"
)

download_model(
    "Qwen/Qwen3-ForcedAligner-0.6B",
    "./models/Qwen3-ForcedAligner-0.6B"
)

download_model(
    "pyannote/speaker-diarization-3.1",
    "./models/pyannote-speaker-diarization-3.1"
)

print("\nВсе модели загружены!")
```

---

## 📥 Способ 2: Ручная загрузка

### Шаг 1: Загрузить модели с Hugging Face

#### Qwen3-ASR-1.7B
1. Открыть: https://huggingface.co/Qwen/Qwen3-ASR-1.7B
2. Кликнуть "Files and versions"
3. Загрузить все файлы (или "Download folder")
4. Распаковать в `./models/Qwen3-ASR-1.7B/`

#### Qwen3-ForcedAligner-0.6B
1. Открыть: https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B
2. Загрузить файлы
3. Распаковать в `./models/Qwen3-ForcedAligner-0.6B/`

#### pyannote-speaker-diarization-3.1
1. Открыть: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Загрузить файлы
3. Распаковать в `./models/pyannote-speaker-diarization-3.1/`

### Шаг 2: Проверка структуры

```
models/
├── Qwen3-ASR-1.7B/
│   ├── config.json
│   ├── generation_config.json
│   ├── pytorch_model.bin
│   ├── scheduler.pt
│   ├── optimizer.pt
│   └── tokenizer.json
├── Qwen3-ForcedAligner-0.6B/
│   ├── config.json
│   ├── pytorch_model.bin
│   └── tokenizer.json
└── pyannote-speaker-diarization-3.1/
    ├── config.json
    ├── pytorch_model.bin
    └── config.yaml
```

---

## 🐳 Способ 3: Docker (автоматическая загрузка)

### Обновленный Dockerfile с загрузкой моделей

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    build-essential python3 python3-pip python3-dev git wget curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Создание директорий
RUN mkdir -p /app/models /app/uploads /app/output /app/logs

# Загрузка моделей (только один раз)
RUN /opt/venv/bin/python3 -c "
import os
os.environ['HF_HUB_OFFLINE'] = '0'
from huggingface_hub import snapshot_download
snapshot_download(repo_id='Qwen/Qwen3-ASR-1.7B', local_dir='/app/models/Qwen3-ASR-1.7B', local_dir_use_symlinks=False)
snapshot_download(repo_id='Qwen/Qwen3-ForcedAligner-0.6B', local_dir='/app/models/Qwen3-ForcedAligner-0.6B', local_dir_use_symlinks=False)
snapshot_download(repo_id='pyannote/speaker-diarization-3.1', local_dir='/app/models/pyannote-speaker-diarization-3.1', local_dir_use_symlinks=False)
"

# Копирование приложения
COPY app/ ./app/
COPY win32/gui/ ./win32/gui/ 2>/dev/null || true

ENV PYTHONUNBUFFERED=1
ENV HF_HUB_OFFLINE=1
ENV HF_OFFLINE=1

EXPOSE 7860
CMD ["/opt/venv/bin/python", "-m", "gradio", "app/main.py"]
```

### Сборка и запуск

```bash
# Сборка (загрузка моделей может занять 10+ минут)
docker build -t qwen-medical-transcriber .

# Запуск
docker-compose up -d
```

---

## ✅ Проверка установки

### Тест через Python

```python
import os
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

# Проверка ASR
try:
    from asr import QwenASRProcessor
    processor = QwenASRProcessor()
    print("✅ ASR модель загружена успешно")
except Exception as e:
    print(f"❌ ASR ошибка: {e}")

# Проверка Diarization
try:
    from diarization import SpeakerDiarization
    diarizer = SpeakerDiarization()
    print("✅ Diarization модель загружена успешно")
except Exception as e:
    print(f"❌ Diarization ошибка: {e}")

# Проверка Aligner
try:
    from aligner import ForcedAligner
    aligner = ForcedAligner()
    print("✅ Aligner модель загружена успешно")
except Exception as e:
    print(f"❌ Aligner ошибка: {e}")
```

### Тест через Web UI

1. Запустить: `python -m app.main`
2. Открыть `http://localhost:7860`
3. Загрузить короткий тестовый WAV файл
4. Нажать "Обработать"

Если обработка прошла успешно — все модели работают!

---

## 📊 Статус загрузки моделей

| Модель | Hugging Face | Размер | Статус |
|--------|-------------|--------|--------|
| Qwen3-ASR-1.7B | [ссылка](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) | ~3.4 GB | ⬜ |
| Qwen3-ForcedAligner-0.6B | [ссылка](https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B) | ~1.2 GB | ⬜ |
| pyannote-speaker-diarization-3.1 | [ссылка](https://huggingface.co/pyannote/speaker-diarization-3.1) | ~250 MB | ⬜ |

---

## 🐛 Устранение проблем

### Проблема: "Model not found"

**Решение:**
- Убедиться, что папка `models/` существует
- Проверить, что в папке `models/Qwen3-ASR-1.7B/` есть файл `config.json`
- Проверить права доступа к папке

### Проблема: Недостаточно места на диске

**Решение:**
- Удалить кэш pip: `pip cache purge`
- Использовать внешний диск для моделей
- Удалить временные файлы

### Проблема: Ошибка загрузки (HF Hub)

**Решение:**
- Проверить интернет-соединение
- Установить переменную `HF_HUB_OFFLINE=0`
- Попробовать загрузить вручную

---

## 📝 Примечания

1. Модели загружаются **только один раз** — после этого система работает офлайн
2. Размер моделей может немного отличаться от указанного
3. Рекомендуется использовать SSD для лучшей производительности
4. GPU ускорение значительно ускоряет обработку

---

**Спасибо за использование Qwen Medical Transcriber!**
