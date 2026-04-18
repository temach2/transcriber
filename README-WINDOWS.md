# Qwen Medical Transcriber — Руководство для Windows

**Полное руководство по установке и использованию на Windows 10/11**

---

## 📋 Содержание

- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
- [Сборка из исходников](#сборка-из-исходников)
- [Устранение проблем](#устранение-проблем)

---

## 🔧 Требования

### Системные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| ОС | Windows 10/11 | Windows 11 |
| CPU | Intel Core i5 / AMD Ryzen 5 | Intel Core i7 / AMD Ryzen 7 |
| RAM | 8 GB | 16 GB |
| GPU (опционально) | Без GPU | NVIDIA GPU с 4GB+ VRAM |
| Диск | 20 GB свободного места | 50 GB |

### Программные требования

- Python 3.10, 3.11 или 3.12
- Administrator права для установки
- NVIDIA drivers (для GPU ускорения)

---

## 🚀 Установка (Pre-built)

### Вариант 1: Установщик (рекомендуется)

1. Скачать `setup-qwen-transcriber.exe`
2. Запустить установку
3. Следовать инструкциям мастера
4. Запустить приложение из меню "Пуск" или рабочего стола

### Вариант 2: Ручная установка

#### Шаг 1: Установка Python

1. Скачать Python 3.11 или 3.12 с [python.org](https://www.python.org/downloads/)
2. Установить с флажком **"Add Python to PATH"**

#### Шаг 2: Установка зависимостей

Открыть PowerShell или CMD и выполнить:

```powershell
# Проверка Python
python --version

# Создание виртуального окружения
python -m venv venv
.\venv\Scripts\activate

# Установка зависимостей
pip install -r requirements-win32.txt
```

#### Шаг 3: Подготовка моделей

Создать папку `models` и загрузить туда модели:

```
models/
├── Qwen3-ASR-1.7B/
├── Qwen3-ForcedAligner-0.6B/
└── pyannote-speaker-diarization-3.1/
```

#### Шаг 4: Запуск

```powershell
python -m win32.gui.main_window
```

---

## 💻 Использование

### Запуск приложения

#### Через меню "Пуск"

1. Открыть меню "Пуск"
2. Найти "Qwen Medical Transcriber"
3. Кликнуть по иконке

#### Через ярлык на рабочем столе

1. Двойной клик по ярлыку "Qwen Medical Transcriber"

#### Через командную строку

```powershell
cd "C:\Program Files\Qwen Medical Transcriber"
QwenTranscriber.exe
```

### Интерфейс приложения

#### Главное окно

![Main Window](resources/screenshot-main.png)

1. **Добавить файл** — загрузить аудио (WAV, MP3, FLAC, M4A, OGG)
2. **Язык** — выбрать язык (Русский/Английский/Авто)
3. **Спикеры** — количество говорящих (1-10)
4. **Forced Alignment** — точные таймкоды ( медленнее, но точнее)
5. **Таймкоды** — включить временные метки
6. **Обработать** — запустить транскрипцию

### Настройки

1. Открыть меню "Файл" → "Настройки"
2. Настроить:
   - Язык по умолчанию
   - Количество спикеров
   - Директории для моделей и результатов
   - Тему интерфейса

### Работа с результатами

-DOCX файл создается в `output/`
- Предпросмотр диалога в окне приложения
- Статус обработки в нижней строке

---

## 🔨 Сборка из исходников

### Подготовка

1. Установить Visual Studio Build Tools
2. Установить Python 3.11
3. Установить CUDA Toolkit (для GPU)

### Шаг 1: Установка зависимостей

```powershell
# Клонировать репозиторий
git clone <repository-url>
cd qwen-medical-transcriber

# Создать виртуальное окружение
python -m venv venv
.\venv\Scripts\activate

# Установить зависимости
pip install -r requirements-win32.txt
```

### Шаг 2: Настройка моделей

Скопировать модели в папку `models/`:

```
models/
├── Qwen3-ASR-1.7B/
├── Qwen3-ForcedAligner-0.6B/
└── pyannote-speaker-diarization-3.1/
```

### Шаг 3: Сборка .exe

#### Способ 1: Использование build.bat

```powershell
cd win32\build
.\build.bat
```

#### Способ 2: PyInstaller вручную

```powershell
# Установить PyInstaller
pip install pyinstaller

# Собрать
pyinstaller --name="QwenTranscriber" ^
    --windowed ^
    --noconsole ^
    --onefile ^
    --add-data="win32/gui;win32/gui" ^
    --add-data="app;app" ^
    --hidden-import=qwen_asr ^
    --hidden-import=transformers ^
    --hidden-import=torch ^
    --icon=win32/resources/icon.ico ^
    win32/gui/main_window.py
```

### Шаг 4: Создание инсталлятора

1. Установить [Inno Setup](https://jrsoftware.org/isdl.php)
2. Открыть `win32/installer/setup.iss`
3. Настроить пути к моделям (если требуется)
4. Скомпилировать (Ctrl+I)

---

## 🔧 Устранение проблем

### Ошибка 1: "Python not found"

**Решение:**
- Установить Python 3.11
- Добавить Python в PATH
- Перезагрузить систему

### Ошибка 2: "ModuleNotFoundError: No module named 'customtkinter'"

**Решение:**
```powershell
pip install customtkinter
pip install Pillow
```

### Ошибка 3: "Torch CUDA not available"

**Решение:**
- Установить CUDA Toolkit 12.1
- Установить NVIDIA drivers
- Переустановить PyTorch с CUDA:
```powershell
pip uninstall torch
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```

### Ошибка 4: "Model not found"

**Решение:**
Создать структуру папок в `models/`:

```
models/
├── Qwen3-ASR-1.7B/
│   ├── config.json
│   ├── pytorch_model.bin
│   └── ...
├── Qwen3-ForcedAligner-0.6B/
│   └── ...
└── pyannote-speaker-diarization-3.1/
    └── ...
```

### Ошибка 5: "Permission denied" при установке

**Решение:**
- Запустить PowerShell от имени администратора
- Отключить антивирус на время установки

### Ошибка 6: Приложение медленно работает

**Решение:**
1. Использовать GPU (NVIDIA)
2. Уменьшить длительность аудио
3. Отключить Forced Alignment
4. Уменьшить количество спикеров

### Ошибка 7: "Failed to load model"

**Решение:**
1. Убедиться, что в папке модели есть все файлы
2. Проверить права доступа к папке
3. Запустить от имени администратора

---

## 📊 Производительность

| Конфигурация | Скорость (1 мин аудио) | Память |
|--------------|------------------------|--------|
| CPU only | ~3-5 минут | ~4 GB |
| GPU (RTX 3060) | ~30-60 сек | ~6 GB |
| GPU (RTX 4090) | ~15-30 сек | ~8 GB |

---

## 📁 Структура файлов (Windows)

```
C:\Program Files\Qwen Medical Transcriber\
├── QwenTranscriber.exe       # Главный executable
├── post_install.exe          # Пост-установочный скрипт
├── resources/                # Иконки и ресурсы
├── models/                   # Модели (если установлены)
├── uploads/                  # Загруженные файлы
├── output/                   # Результаты
└── logs/                     # Логи

%APPDATA%\Qwen Medical Transcriber\
└── settings.json             # Настройки
```

---

## 🔐 Безопасность

- Все данные обрабатываются локально
- Нет внешних сетевых соединений
- Модели не загружаются из интернета
- Логи не содержат конфиденциальную информацию

---

## 📞 Поддержка

### Документация

- [Глобальная документация](README.md)
- [Настройка для Docker](docker-compose.yml)
- [API документация](app/)

### Получение помощи

1. Проверить раздел "Устранение проблем" выше
2. Посмотреть логи в `logs/`
3. Создать issue на GitHub

---

## 📜 Лицензия

MIT License

---

**Qwen Medical Transcriber v2.0.0**
*Офлайн система транскрипции медицинских консультаций*
