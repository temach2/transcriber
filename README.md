# Qwen Medical Transcriber

**Профессиональная система офлайн транскрипции медицинских консультаций с разделением диалога по ролям**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-green.svg)](https://www.microsoft.com/)
[![Gradio](https://img.shields.io/badge/Interface-Gradio%20%7C%20CustomTkinter-orange.svg)](https://gradio.app/)

---

## 📋 Содержание

- [Быстрый старт](#-быстрый-старт)
- [Требования](#-требования)
- [Установка](#-установка)
- [Настройка моделей](#-настройка-моделей)
- [Использование](#-использование)
- [Сборка .exe файла](#-сборка-exe-файла)
- [Проблемы и решения](#-проблемы-и-решения)
- [Структура проекта](#-структура-проекта)

---

## 🚀 Быстрый старт (Visual Studio Code)

### 1. Открытие проекта в VS Code

```powershell
# В PowerShell или CMD выполните:
code .
```

Или откройте VS Code и выберите `File > Open Folder`, затем укажите папку `D:\botsdevelopment\med-transcriber`.

### 2. Создание виртуального окружения

```powershell
# В папке проекта (в VS Code это делается в терминале: Ctrl+`)
python -m venv venv
```

### 3. Активация виртуального окружения

```powershell
# Для PowerShell:
.\venv\Scripts\Activate.ps1

# Для CMD:
venv\Scripts\activate.bat
```

**Примечание:** Если получаете ошибку выполнения скриптов, выполните:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Установка зависимостей

```powershell
# Установка основных зависимостей (Gradio Web UI + processor)
pip install -r requirements.txt

# ИЛИ для Windows GUI (CustomTkinter)
pip install -r requirements-win32.txt
```

### 5. Подготовка моделей

Создайте структуру папок `models/` и загрузите туда модели:

```
models/
├── Qwen3-ASR-1.7B/
├── Qwen3-ForcedAligner-0.6B/
└── pyannote-speaker-diarization-3.1/
```

> **Важно:** Модели не включены в репозиторий. Скачайте их с Hugging Face (см. [Настройка моделей](#-настройка-моделей)).

### 6. Запуск Gradio Web UI

```powershell
# В терминале VS Code (убедитесь, что venv активирован):
python -m app.main
```

Откроется в браузере: `http://localhost:7860`

---

## 📋 Требования

### Системные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| ОС | Windows 10/11 | Windows 11 |
| CPU | Intel Core i5 / AMD Ryzen 5 | Intel Core i7 / AMD Ryzen 7 |
| RAM | 8 GB | 16 GB |
| GPU (опционально) | Без GPU | NVIDIA GPU с 4GB+ VRAM |
| Диск | 20 GB свободного места | 50 GB |

### Программные требования

- **Python 3.10, 3.11 или 3.12**
- **pip** (стандартно входит в Python)
- **Git** (опционально для клонирования репозитория)

### GPU поддержка (опционально)

Для ускорения обработки на NVIDIA GPU:

```powershell
# Установить CUDA Toolkit 12.1
# Затем установить PyTorch с CUDA:
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```

---

## 🔧 Установка

### Способ 1: Установка через pip (рекомендуется)

```powershell
# Клонировать репозиторий (если используется git)
git clone <repository-url>
cd D:\botsdevelopment\med-transcriber

# Создать виртуальное окружение
python -m venv venv
.\venv\Scripts\activate

# Установить зависимости
pip install -r requirements-win32.txt
```

### Способ 2: Ручная установка зависимостей

```powershell
# Проверить версию Python
python --version

# Установить основные библиотеки
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate qwen-asr>=0.0.6
pip install pyannote.audio pyannote.core
pip install python-docx gradio
pip install python-dotenv loguru tqdm pyyaml
pip install soundfile audioread librosa

# Для Windows GUI
pip install customtkinter Pillow pystray pyinstaller pywin32
```

---

## 🤖 Настройка моделей

Модели необходимо загрузить вручную из Hugging Face.

### Скачивание моделей

#### 1. ASR модель (Qwen3-ASR-1.7B)

**Hugging Face:** [Qwen/Qwen3-ASR-1.7B](https://huggingface.co/Qwen/Qwen3-ASR-1.7B)

```powershell
# Скачать через Python
pip install huggingface-cli
huggingface-cli download Qwen/Qwen3-ASR-1.7B --local-dir ./models/Qwen3-ASR-1.7B
```

**Альтернативно через браузер:**
1. Открыть ссылку выше
2. Нажать `Files and versions`
3. Скачать все файлы в папку `./models/Qwen3-ASR-1.7B/`

#### 2. Diarization модель (pyannote 3.1)

**Hugging Face:** [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)

```powershell
huggingface-cli download pyannote/speaker-diarization-3.1 --local-dir ./models/pyannote-speaker-diarization-3.1
```

#### 3. Aligner модель (Qwen3-ForcedAligner-0.6B)

**Hugging Face:** [Qwen/Qwen3-ForcedAligner-0.6B](https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B)

```powershell
huggingface-cli download Qwen/Qwen3-ForcedAligner-0.6B --local-dir ./models/Qwen3-ForcedAligner-0.6B
```

### Структура папки models

После загрузки должна получиться такая структура:

```
D:\botsdevelopment\med-transcriber\
├── models/
│   ├── Qwen3-ASR-1.7B/
│   │   ├── config.json
│   │   ├── generation_config.json
│   │   ├── pytorch_model.bin
│   │   ├── tokenizer.json
│   │   └── ...
│   ├── pyannote-speaker-diarization-3.1/
│   │   ├── config.yaml
│   │   ├── pytorch_model.bin
│   │   └── ...
│   └── Qwen3-ForcedAligner-0.6B/
│       ├── config.json
│       ├── pytorch_model.bin
│       └── ...
```

### Проверка моделей

После настройки моделей запустите тест:

```powershell
python -c "from app.asr import QwenASRProcessor; p = QwenASRProcessor(); print('ASR OK')"
python -c "from app.diarization import SpeakerDiarization; d = SpeakerDiarization(); print('Diarization OK')"
```

---

## 💻 Использование

### Вариант 1: Gradio Web UI (рекомендуется для разработки)

```powershell
# Запустить веб-интерфейс
python -m app.main
```

**Особенности:**
- Удобный веб-интерфейс
- Потоковая передача прогресса
- Предпросмотр диалога
- Массовая обработка

**URL:** `http://localhost:7860`

---

### Вариант 2: Windows Desktop App

```powershell
# Запустить CustomTkinter приложение
python -m win32.gui.main_window
```

**Особенности:**
- Нативное оконное приложение
- Системный трей
- Drag & drop файлов
- Многопоточная обработка

---

### Вариант 3: CLI обработка (для automation)

```powershell
# Обработка одного файла
python -m app.processor "C:\path\to\audio.wav" "C:\path\to\output.docx"

# С параметрами
python -m app.processor input.wav --language ru --speakers 2 --alignment
```

---

### Вариант 4: Docker

```bash
# Сборка образа
docker build -t qwen-medical-transcriber .

# Запуск с GPU
docker run --gpus all -p 7860:7860 \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/uploads:/app/uploads:rw \
  -v $(pwd)/output:/app/output:rw \
  qwen-medical-transcriber
```

---

## 🔨 Сборка .exe файла (Windows)

### Предварительные требования

1. **Python 3.10-3.12**
2. **Установлены зависимости из requirements-win32.txt**
3. **Visual Studio Build Tools** (для компиляции некоторых пакетов)

### Шаг 1: Установка зависимостей

```powershell
# Активировать venv
.\venv\Scripts\activate

# Установить зависимости
pip install -r requirements-win32.txt
```

### Шаг 2: Сборка через build.bat (рекомендуется)

```powershell
# Перейти в папку сборки
cd win32\build

# Запустить скрипт сборки
.\build.bat
```

**Результат:** `dist\QwenTranscriber.exe`

---

### Шаг 3: Сборка вручную (для кастомизации)

```powershell
# Установить PyInstaller (если не установлен)
pip install pyinstaller

# Перейти в папку сборки
cd win32\build

# Сборка (одна команда)
pyinstaller --name="QwenTranscriber" ^
    --windowed ^
    --noconsole ^
    --onefile ^
    --add-data="win32/gui;win32/gui" ^
    --add-data="app;app" ^
    --hidden-import=qwen_asr ^
    --hidden-import=transformers ^
    --hidden-import=torch ^
    --hidden-import=pyannote ^
    --icon=win32/resources/icon.ico ^
    --add-data="models;models" ^
    ../gui/main_window.py
```

**Ключи:**
- `--windowed` — без консольного окна
- `--noconsole` — скрыть консоль
- `--onefile` — собрать в один файл
- `--add-data` — добавить данные (формат: `source;destination`)
- `--hidden-import` — добавить скрытые импорты
- `--icon` — иконка приложения

---

### Шаг 4: Создание инсталлятора (Inno Setup)

1. **Установить Inno Setup** — [https://jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php)

2. **Открыть скрипт:**
   ```
   win32/installer/setup.iss
   ```

3. **Настроить пути (если нужно):**
   ```ini
   #define MyAppName "Qwen Medical Transcriber"
   #define MyAppVersion "1.0.0"
   #define MyAppExeName "QwenTranscriber.exe"
   #define MyAppPublisher "Qwen Medical"
   #define MyAppUrl "https://github.com/qwen-medical/transcriber"
   #define AppPath "dist\"
   ```

4. **Скомпилировать:** `Ctrl+I`

**Результат:** `Output\Setup.exe`

---

## ⚠️ Проблемы и решения

### Ошибка 1: "Python not found"

**Решение:**
```powershell
# Проверить установку Python
python --version

# Если не найден, добавить в PATH:
# 1. Скачать Python с python.org
# 2. При установке выбрать "Add Python to PATH"
```

---

### Ошибка 2: "ModuleNotFoundError: No module named 'customtkinter'"

**Решение:**
```powershell
pip install customtkinter
pip install Pillow
```

---

### Ошибка 3: "Torch CUDA not available"

**Решение:**
```powershell
# Проверить версию CUDA
nvidia-smi

# Переустановить PyTorch с CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```

---

### Ошибка 4: "Model not found"

**Решение:**
Создать структуру папок:

```
models/
├── Qwen3-ASR-1.7B/
│   ├── config.json
│   ├── generation_config.json
│   ├── pytorch_model.bin
│   └── ...
├── pyannote-speaker-diarization-3.1/
│   ├── config.yaml
│   └── pytorch_model.bin
└── Qwen3-ForcedAligner-0.6B/
    ├── config.json
    └── pytorch_model.bin
```

---

### Ошибка 5: "Permission denied" при установке

**Решение:**
```powershell
# Запустить PowerShell от имени администратора
# Или использовать --user флаг
pip install --user <package>
```

---

### Ошибка 6: Приложение медленно работает

**Решение:**
1. Использовать GPU (NVIDIA)
2. Уменьшить длительность аудио
3. Отключить Forced Alignment
4. Уменьшить количество спикеров

---

### Ошибка 7: "Failed to load model"

**Решение:**
1. Убедиться, что в папке модели есть все файлы
2. Проверить права доступа к папке
3. Запустить от имени администратора
4. Попробовать перескачать модель

---

### Ошибка 8: "qwen_asr not installed"

**Решение:**
```powershell
pip install qwen-asr>=0.0.6
```

---

## 📁 Структура проекта

```
D:\botsdevelopment\med-transcriber\
├── app/                              # Основное приложение (processor, ASR, etc.)
│   ├── __init__.py
│   ├── main.py                      # Gradio Web UI
│   ├── processor.py                 # Оркестратор пайплайна
│   ├── audio_converter.py           # Конвертация аудио (16kHz WAV)
│   ├── asr.py                       # Qwen3-ASR-1.7B транскрипция
│   ├── diarization.py               # PyAnnote 3.1 диаризация
│   ├── aligner.py                   # Forced Aligner 0.6B
│   ├── docx_generator.py            # Генератор Word документов
│   └── utils.py                     # Утилиты (логирование, конфиги)
│
├── win32/                           # Windows компоненты
│   ├── gui/                         # CustomTkinter интерфейс
│   │   ├── __init__.py
│   │   ├── styles.py                # Темы и стили
│   │   ├── main_window.py           # Главное окно приложения
│   │   ├── settings_window.py       # Окно настроек
│   │   └── progress_dialog.py       # Диалог прогресса
│   ├── installer/                   # Inno Setup инсталлятор
│   │   ├── setup.iss                # Inno Setup скрипт
│   │   ├── installer_config.py      # Конфиг генерации
│   │   └── post_install.py          # Пост-установочный скрипт
│   └── build/                       # PyInstaller конфигурация
│       ├── build.bat                # Скрипт сборки (.exe)
│       └── pyinstaller.spec         # Конфигурация PyInstaller
│
├── models/                          # Модели (не включены в репозиторий)
│   ├── Qwen3-ASR-1.7B/
│   ├── Qwen3-ForcedAligner-0.6B/
│   └── pyannote-speaker-diarization-3.1/
│
├── uploads/                         # Загруженные файлы
│   └── converted/                   # Кэш конвертированных WAV
│
├── output/                          # Сгенерированные DOCX
│
├── logs/                            # Логи работы
│   ├── app.log
│   └── win32.log
│
├── requirements.txt                 # Зависимости для Linux/macOS
├── requirements-win32.txt           # Зависимости для Windows GUI
├── setup.py                         # Установка пакета
├── .env.example                     # Пример конфигурации
├── .gitignore                       # Исключения Git
├── README.md                        # Этот файл
└── CLAUDE.md                        # Инструкции для Claude Code
```

---

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Hugging Face — офлайн режим
HF_OFFLINE=1
HF_HUB_OFFLINE=1

# Gradio Web UI
GRADIO_PORT=7860
GRADIO_SHARE=false
GRADIO_HOST=0.0.0.0

# Уровень логов
LOG_LEVEL=INFO

# Настройки аудио
TARGET_SAMPLE_RATE=16000
DEFAULT_NUM_SPEAKERS=2
MIN_SPEAKERS=1
MAX_SPEAKERS=5

# Директории
OUTPUT_DIR=./output
UPLOADS_DIR=./uploads
MODELS_DIR=./models
LOGS_DIR=./logs

# Языки
SUPPORTED_LANGUAGES=ru,en
DEFAULT_LANGUAGE=ru
```

---

## 📝 Лицензия

MIT License — см. [LICENSE](LICENSE) для подробной информации.

---

## 🙏 Благодарности

- [Qwen](https://github.com/QwenLM/Qwen) — за ASR модели
- [PyAnnote](https://github.com/pyannote/pyannote.audio) — за диаризацию
- [Hugging Face](https://huggingface.co/) — за инфраструктуру
- [Gradio](https://github.com/gradio-app/gradio) — за Web UI
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — за Windows GUI

---

## 📞 Поддержка

- **GitHub Issues:** [report issue](https://github.com/qwen-medical/transcriber/issues)
- **Documentation:** [wiki](https://github.com/qwen-medical/transcriber/wiki)
- **Email:** support@qwen-medical.example.com

---

## 📚 Дополнительная документация

- [Windows GUI Guide](README-WINDOWS.md) — Подробное руководство для Windows
- [Models Installation](MODELS-INSTALLATION.md) — Инструкция по установке моделей

---

**© 2026 Qwen Medical Transcriber**
*Офлайн система транскрипции медицинских консультаций*
