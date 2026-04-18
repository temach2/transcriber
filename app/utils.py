"""
Utils Module
Helper functions for the medical transcriber application.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from loguru import logger

# Установка офлайн-режима Hugging Face
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

logger.info("Utils module initialized")


def setup_logging(
    log_dir: str = None,
    log_level: str = None,
    log_format: str = None
):
    """
    Настроить логгирование.

    Args:
        log_dir: Директория для логов
        log_level: Уровень логирования
        log_format: Формат логов
    """
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')

    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')

    # Удалить старые обработчики
    logger.remove()

    # Формат по умолчанию
    if log_format is None:
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <blue>{name}</blue>:<blue>{function}</blue>:<blue>{line}</blue> - <level>{message}</level>"

    # Консольный обработчик
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )

    # Файловый обработчик
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d')}.log")

        logger.add(
            log_file,
            format=log_format,
            level=log_level,
            rotation="1 day",
            retention="7 days",
            compression="zip"
        )

    logger.info(f"Логгирование настроено: {log_dir}, level={log_level}")


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Получить информацию о файле.

    Args:
        file_path: Путь к файлу

    Returns:
        Словарь с информацией о файле
    """
    if not os.path.exists(file_path):
        return {'error': 'Файл не найден'}

    stat = os.stat(file_path)
    ext = Path(file_path).suffix.lower()

    return {
        'name': os.path.basename(file_path),
        'path': os.path.abspath(file_path),
        'size': stat.st_size,
        'size_human': format_file_size(stat.st_size),
        'extension': ext,
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


def format_file_size(size_bytes: int) -> str:
    """Форматировать размер файла в читаемый вид."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds: float) -> str:
    """Форматировать длительность в читаемый вид."""
    if seconds < 60:
        return f"{seconds:.1f} сек"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}:{minutes:02d}"


def get_audio_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Получить список аудио файлов в директории.

    Args:
        directory: Директория для поиска
        extensions: Список расширений (по умолчанию: все поддерживаемые)

    Returns:
        Список путей к аудио файлам
    """
    if extensions is None:
        extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.oga', '.opus']

    files = []
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            if Path(filename).suffix.lower() in extensions:
                files.append(os.path.join(directory, filename))

    return sorted(files)


def validate_audio_file(file_path: str) -> Dict[str, Any]:
    """
    Проверить валидность аудио файла.

    Args:
        file_path: Путь к файлу

    Returns:
        {
            'valid': bool,
            'error': str (если ошибка)
        }
    """
    if not os.path.exists(file_path):
        return {'valid': False, 'error': 'Файл не найден'}

    # Проверка размера
    size = os.path.getsize(file_path)
    if size < 100:  # Минимальный размер 100 байт
        return {'valid': False, 'error': 'Файл слишком мал'}

    if size > 500 * 1024 * 1024:  # Максимальный размер 500 MB
        return {'valid': False, 'error': 'Файл слишком большой (максимум 500 MB)'}

    # Попытка открыть файл
    try:
        import soundfile as sf
        with sf.SoundFile(file_path) as f:
            if f.frames == 0:
                return {'valid': False, 'error': 'Аудио файл пустой'}
            if f.samplerate < 8000 or f.samplerate > 192000:
                return {'valid': False, 'error': 'Недопустимая частота дискретизации'}
        return {'valid': True}
    except Exception as e:
        return {'valid': False, 'error': f'Ошибка чтения файла: {str(e)}'}


def create_directory_structure(base_path: str = None) -> Dict[str, str]:
    """
    Создать необходимую структуру директорий.

    Args:
        base_path: Базовая директория

    Returns:
        Словарь с путями к созданным директориям
    """
    if base_path is None:
        base_path = os.path.dirname(__file__)

    structure = {
        'base': base_path,
        'models': os.path.join(base_path, 'models'),
        'output': os.path.join(base_path, 'output'),
        'uploads': os.path.join(base_path, 'uploads'),
        'converted': os.path.join(base_path, 'uploads', 'converted'),
        'logs': os.path.join(base_path, 'logs'),
    }

    # Создание директорий
    for key, path in structure.items():
        os.makedirs(path, exist_ok=True)

    return structure


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Загрузить конфигурацию из файла или переменных окружения.

    Args:
        config_path: Путь к файлу конфигурации (.env или .json)

    Returns:
        Словарь с конфигурацией
    """
    config = {}

    # Попытка загрузить .env файл
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', '.env')

    if os.path.exists(config_path):
        ext = Path(config_path).suffix.lower()
        if ext == '.env':
            # Парсинг .env файла
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        elif ext == '.json':
            with open(config_path, 'r') as f:
                config.update(json.load(f))

    # Переопределение из переменных окружения
    env_mappings = {
        'GRADIO_PORT': ('GRADIO_PORT', int),
        'LOG_LEVEL': ('LOG_LEVEL', str),
        'TARGET_SAMPLE_RATE': ('TARGET_SAMPLE_RATE', int),
        'DEFAULT_NUM_SPEAKERS': ('DEFAULT_NUM_SPEAKERS', int),
    }

    for key, (env_key, type_func) in env_mappings.items():
        if env_key in os.environ:
            try:
                config[key] = type_func(os.environ[env_key])
            except (ValueError, TypeError):
                pass

    return config


def get_model_paths(config: Dict = None) -> Dict[str, str]:
    """
    Получить пути к моделям.

    Args:
        config: Конфигурация

    Returns:
        Словарь с путями к моделям
    """
    if config is None:
        config = load_config()

    models_dir = config.get('MODELS_DIR', './models')

    return {
        'asr': os.path.join(models_dir, 'Qwen3-ASR-1.7B'),
        'aligner': os.path.join(models_dir, 'Qwen3-ForcedAligner-0.6B'),
        'diarization': os.path.join(models_dir, 'pyannote-speaker-diarization-3.1'),
    }


def check_models_exist(model_paths: Dict[str, str] = None, config: Dict = None) -> Dict[str, bool]:
    """
    Проверить существование моделей.

    Args:
        model_paths: Пути к моделям
        config: Конфигурация

    Returns:
        Словарь с результатами проверки
    """
    if model_paths is None:
        model_paths = get_model_paths(config)

    results = {}
    for name, path in model_paths.items():
        results[name] = os.path.exists(path)

    return results


def convert_seconds_to_timestamp(seconds: float) -> str:
    """Конвертировать секунды в формат MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def merge_audio_files(input_files: List[str], output_path: str) -> bool:
    """
    Объединить несколько аудио файлов в один.

    Args:
        input_files: Список входных файлов
        output_path: Выходной файл

    Returns:
        True если успешно, иначе False
    """
    try:
        import soundfile as sf
        import numpy as np

        # Считать все файлы
        audios = []
        sample_rate = None

        for file_path in input_files:
            audio, sr = sf.read(file_path)
            if sample_rate is None:
                sample_rate = sr
            elif sample_rate != sr:
                # Ресемплинг при необходимости
                audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)

            audios.append(audio)

        # Объединить
        combined = np.concatenate(audios)

        # Сохранить
        sf.write(output_path, combined, sample_rate)
        return True

    except Exception as e:
        logger.error(f"Ошибка объединения аудио: {e}")
        return False


class ProgressCallback:
    """Класс для callback функций прогресса."""

    def __init__(self, callback: Callable = None):
        """Инициализация callback."""
        self.callback = callback

    def __call__(self, message: str, progress: float = None):
        """Вызвать callback."""
        if self.callback:
            self.callback(message, progress)

    def set_callback(self, callback: Callable):
        """Установить новый callback."""
        self.callback = callback


def safe_import(module_name: str, package_name: str = None) -> Optional[Any]:
    """
    Безопасно импортировать модуль.

    Args:
        module_name: Имя модуля
        package_name: Имя пакета (опционально)

    Returns:
        Импортированный модуль или None при ошибке
    """
    try:
        if package_name:
            return __import__(package_name)
        return __import__(module_name)
    except ImportError:
        return None


if __name__ == "__main__":
    # Тест функций
    print("Testing utils module...")
    print(f"File size: {format_file_size(1234567)}")
    print(f"Duration: {format_duration(3675)}")

    # Создание структуры
    structure = create_directory_structure()
    print(f"Directory structure created:")
    for key, path in structure.items():
        print(f"  {key}: {path}")
