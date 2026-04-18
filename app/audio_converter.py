"""
Audio Converter Module
Converts any audio format to 16kHz Mono WAV with normalization.
All processing is offline - no external API calls.
"""

import os
import tempfile
import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple

import soundfile as sf
import librosa
import numpy as np
from loguru import logger

# Установка офлайн-режима Hugging Face
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

# Настройки по умолчанию
TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1
TARGET_FORMAT = 'wav'
TARGET_SUBTYPE = 'PCM_16'
TARGET_RMS_DB = -20  # -20 dB RMS
TARGET_RMS_VALUE = 0.1  # Соответствует -20 dB

logger.info("Audio converter initialized in OFFLINE mode")


class AudioConverter:
    """Конвертер аудио в формат 16kHz Mono WAV с нормализацией."""

    def __init__(
        self,
        target_sample_rate: int = TARGET_SAMPLE_RATE,
        target_channels: int = TARGET_CHANNELS,
        target_rms_db: float = TARGET_RMS_DB
    ):
        """
        Инициализация конвертера.

        Args:
            target_sample_rate: Целевая частота дискретизации (по умолчанию 16000)
            target_channels: Количество каналов (по умолчанию 1 - Mono)
            target_rms_db: Целевая громкость в dB RMS (по умолчанию -20)
        """
        self.target_sample_rate = target_sample_rate
        self.target_channels = target_channels
        self.target_rms_value = 10 ** (target_rms_db / 20)  # Преобразование dB в значение

        # Допустимые расширения файлов
        self.supported_formats = {
            '.wav': 'wav',
            '.mp3': 'mp3',
            '.flac': 'flac',
            '.m4a': 'm4a',
            '.ogg': 'ogg',
            '.oga': 'oga',
            '.opus': 'opus',
            '.webm': 'webm',
        }

        logger.debug(f"AudioConverter initialized: {target_sample_rate}Hz, {target_channels}ch, {target_rms_db}dB RMS")

    def get_file_extension(self, file_path: str) -> str:
        """Получить расширение файла без точки."""
        return Path(file_path).suffix.lower()

    def is_supported_format(self, file_path: str) -> bool:
        """Проверить, поддерживается ли формат файла."""
        ext = self.get_file_extension(file_path)
        return ext in self.supported_formats

    def calculate_rms(self, audio: np.ndarray) -> float:
        """Рассчитать RMS (Root Mean Square) значения аудио."""
        return np.sqrt(np.mean(audio ** 2))

    def normalize_audio(self, audio: np.ndarray, target_rms: float) -> np.ndarray:
        """
        Нормализовать аудио до целевого RMS значения.

        Args:
            audio: Входной аудиосигнал
            target_rms: Целевое RMS значение

        Returns:
            Нормализованный аудиосигнал
        """
        current_rms = self.calculate_rms(audio)
        if current_rms == 0:
            return audio
        return audio * (target_rms / current_rms)

    def convert_to_wav(
        self,
        input_path: str,
        output_path: str,
        normalize: bool = True,
        progress_callback=None
    ) -> Tuple[str, Optional[float]]:
        """
        Конвертировать аудио файл в 16kHz Mono WAV с нормализацией.

        Args:
            input_path: Путь к входному файлу
            output_path: Путь к выходному файлу
            normalize: Нормализовать ли громкость
            progress_callback: Опциональный callback для отображения прогресса

        Returns:
            Кортеж (output_path, duration_seconds) или (None, None) при ошибке

        Raises:
            FileNotFoundError: Если входной файл не найден
            RuntimeError: Если ошибка при обработке аудио
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Файл не найден: {input_path}")

        ext = self.get_file_extension(input_path)
        if ext not in self.supported_formats:
            raise ValueError(f"Неподдерживаемый формат: {ext}. Поддерживаемые: {list(self.supported_formats.keys())}")

        try:
            # Загрузка аудио
            if ext in ['.mp3', '.m4a', '.ogg', '.oga', '.opus', '.webm']:
                # Для mp3/m4a/ogg используем librosa для ресемплинга
                if progress_callback:
                    progress_callback("Загрузка аудио...")
                audio, sr = librosa.load(input_path, sr=None, mono=True)
            else:
                # Для WAV/FLAC используем soundfile
                if progress_callback:
                    progress_callback("Загрузка аудио...")
                audio, sr = sf.read(input_path)
                # Если стерео, конвертируем в моно
                if audio.ndim > 1:
                    if progress_callback:
                        progress_callback("Конвертация в Mono...")
                    audio = np.mean(audio, axis=1)

            # Ресемплинг, если необходимо
            if sr != self.target_sample_rate:
                if progress_callback:
                    progress_callback(f"Ресемплинг: {sr}Hz → {self.target_sample_rate}Hz...")
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sample_rate)

            # Нормализация
            if normalize:
                if progress_callback:
                    progress_callback(f"Нормализация: {self.target_rms_db}dB RMS...")
                audio = self.normalize_audio(audio, self.target_rms_value)

            # Сохранение в WAV
            if progress_callback:
                progress_callback(f"Сохранение: {output_path}...")

            # Убедиться, что output_path имеет расширение .wav
            output_path = Path(output_path)
            if output_path.suffix.lower() != '.wav':
                output_path = output_path.with_suffix('.wav')

            sf.write(
                str(output_path),
                audio,
                self.target_sample_rate,
                subtype=TARGET_SUBTYPE
            )

            # Получить длительность
            duration = len(audio) / self.target_sample_rate

            logger.info(f"Аудио конвертировано: {input_path} → {output_path} ({duration:.2f}s)")
            return str(output_path), duration

        except Exception as e:
            logger.error(f"Ошибка конвертации {input_path}: {e}")
            raise RuntimeError(f"Ошибка конвертации: {e}") from e

    def convert_with_cache(
        self,
        input_path: str,
        cache_dir: str,
        normalize: bool = True,
        progress_callback=None
    ) -> Tuple[str, Optional[float]]:
        """
        Конвертировать аудио с кэшированием результата.

        Args:
            input_path: Путь к входному файлу
            cache_dir: Директория для кэша
            normalize: Нормализовать ли громкость
            progress_callback: Callback для прогресса

        Returns:
            Кортеж (output_path, duration_seconds)
        """
        # Создать хеш имени файла для кэша
        file_hash = hashlib.md5(Path(input_path).resolve().as_bytes()).hexdigest()[:8]
        original_name = Path(input_path).stem
        cache_filename = f"{original_name}_{file_hash}.wav"
        cache_path = os.path.join(cache_dir, cache_filename)

        # Проверить кэш
        if os.path.exists(cache_path):
            # Проверить, не устарел ли кэш
            input_mtime = os.path.getmtime(input_path)
            cache_mtime = os.path.getmtime(cache_path)
            if input_mtime <= cache_mtime:
                logger.info(f"Взят из кэша: {cache_path}")
                duration = self._get_duration(cache_path)
                return cache_path, duration

        # Создать директорию кэша, если её нет
        os.makedirs(cache_dir, exist_ok=True)

        # Конвертировать
        return self.convert_to_wav(input_path, cache_path, normalize, progress_callback)

    def _get_duration(self, file_path: str) -> Optional[float]:
        """Получить длительность аудио файла."""
        try:
            with sf.SoundFile(file_path) as f:
                return f.frames / f.samplerate
        except Exception:
            return None

    def clear_cache(self, cache_dir: str, max_age_days: int = 7) -> int:
        """
        Очистить кэш конвертированных файлов по возрасту.

        Args:
            cache_dir: Директория кэша
            max_age_days: Максимальный возраст файла в днях

        Returns:
            Количество удаленных файлов
        """
        if not os.path.exists(cache_dir):
            return 0

        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        removed_count = 0

        for filename in os.listdir(cache_dir):
            if filename.endswith('.wav'):
                file_path = os.path.join(cache_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    removed_count += 1
                    logger.debug(f"Удален устаревший кэш: {filename}")

        logger.info(f"Очищено {removed_count} файлов из кэша")
        return removed_count


def convert_audio(
    input_path: str,
    output_dir: str = None,
    normalize: bool = True,
    progress_callback=None
) -> Tuple[str, Optional[float]]:
    """
    Упрощенная функция конвертации аудио.

    Args:
        input_path: Путь к входному файлу
        output_dir: Директория для выходного файла (по умолчанию uploads/converted)
        normalize: Нормализовать ли громкость
        progress_callback: Callback для прогресса

    Returns:
        Кортеж (output_path, duration_seconds)
    """
    converter = AudioConverter()
    output_dir = output_dir or os.path.join(os.path.dirname(__file__), '..', 'uploads', 'converted')
    os.makedirs(output_dir, exist_ok=True)

    return converter.convert_to_wav(input_path, output_dir, normalize, progress_callback)


if __name__ == "__main__":
    # Тестовая функция
    import sys

    if len(sys.argv) < 2:
        print("Использование: python audio_converter.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    converter = AudioConverter()

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'converted')
    os.makedirs(output_dir, exist_ok=True)

    try:
        output_path, duration = converter.convert_to_wav(input_file, output_dir)
        print(f"Конвертировано: {output_path}")
        print(f"Длительность: {duration:.2f} секунд")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
