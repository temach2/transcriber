"""
ASR Module (Automatic Speech Recognition)
Uses Qwen3-ASR-1.7B model for speech-to-text transcription.
All processing is offline with local models.
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any

import torch
from loguru import logger

# Установка офлайн-режима Hugging Face ДО импорта any huggingface libraries
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

try:
    from qwen_asr import Qwen3ASRModel
except ImportError:
    logger.warning("qwen_asr не установлен, использование fallback режима")
    Qwen3ASRModel = None

# Допустимые языки
SUPPORTED_LANGUAGES = ['ru', 'en']
DEFAULT_LANGUAGE = 'ru'

# Маппинг языков для Qwen ASR
LANGUAGE_MAP = {
    'ru': 'ru',
    'en': 'en',
    'russian': 'ru',
    'english': 'en',
}

logger.info("ASR module initialized in OFFLINE mode")


class QwenASRProcessor:
    """Обработчик ASR с использованием локальной модели Qwen3-ASR-1.7B."""

    def __init__(
        self,
        model_path: str = None,
        device: str = None,
        dtype: str = 'float16',
        local_files_only: bool = True
    ):
        """
        Инициализация ASR процессора.

        Args:
            model_path: Путь к локальной модели (по умолчанию ./models/Qwen3-ASR-1.7B)
            device: Устройство для inference ('cuda' или 'cpu')
            dtype: Тип данных ('float16' или 'float32')
            local_files_only: Использовать только локальные файлы
        """
        # Определение пути к модели
        self.model_path = model_path
        if self.model_path is None:
            # Относительный путь от текущего модуля
            self.model_path = os.path.join(
                os.path.dirname(__file__), '..', 'models', 'Qwen3-ASR-1.7B'
            )
        self.model_path = os.path.abspath(self.model_path)

        # Определение устройства
        self.device = device
        if self.device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Определение типа данных
        self.dtype = dtype
        self.torch_dtype = torch.float16 if dtype == 'float16' and self.device == 'cuda' else torch.float32

        # Модель и processor
        self.model = None
        self.processor = None

        # Инициализация
        self._initialize_model(local_files_only)

        logger.info(f"QwenASRProcessor initialized: device={self.device}, dtype={dtype}")

    def _initialize_model(self, local_files_only: bool = True) -> bool:
        """
        Инициализация модели Qwen ASR.

        Returns:
            True если модель успешно загружена, иначе False
        """
        if Qwen3ASRModel is None:
            logger.error("Библиотека qwen_asr не установлена")
            return False

        try:
            logger.info(f"Загрузка модели из: {self.model_path}")

            # Проверка существования модели
            if not os.path.exists(self.model_path):
                logger.error(f"Модель не найдена: {self.model_path}")
                return False

            # Загрузка модели
            self.model = Qwen3ASRModel.from_pretrained(
                self.model_path,
                dtype=self.torch_dtype,
                device_map=self.device,
                local_files_only=local_files_only
            )

            logger.info("Модель Qwen3-ASR-1.7B успешно загружена")
            return True

        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            self.model = None
            return False

    def transcribe(
        self,
        audio_path: str,
        language: str = None,
        temperature: float = 0.0,
        beam_size: int = 5,
        use_vad: bool = True,
        return_timestamps: bool = True
    ) -> Dict[str, Any]:
        """
        Транскрибировать аудио файл в текст.

        Args:
            audio_path: Путь к аудио файлу (WAV 16kHz рекомендуется)
            language: Язык ('ru', 'en' или 'auto' для автоматического определения)
            temperature: Температура для генерации (0 = детерминированное)
            beam_size: Размер beam search
            use_vad: Использовать ли VAD (Voice Activity Detection)
            return_timestamps: Возвращать ли таймкоды

        Returns:
            Словарь с результатами:
            {
                'text': str,
                'language': str,
                'segments': List[dict] (опционально),
                'duration': float (опционально)
            }
        """
        if self.model is None:
            raise RuntimeError("Модель не инициализирована. Вызовите _initialize_model().")

        # Нормализация языка
        language = language or DEFAULT_LANGUAGE
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE

        # Длительность аудио
        audio_duration = self._get_audio_duration(audio_path)

        try:
            # Выполнение транскрипции
            result = self.model.transcribe(
                audio_path,
                language=language if language != 'auto' else None,
                temperature=temperature,
                beam_size=beam_size,
                vad=use_vad,
                timestamp=return_timestamps
            )

            # Парсинг результата
            output = {
                'text': result.get('text', ''),
                'language': language,
                'duration': audio_duration,
            }

            # Если есть сегменты с таймкодами
            if return_timestamps and 'segments' in result:
                output['segments'] = self._parse_segments(result['segments'])

            logger.info(f"Транскрипция завершена: {len(output['text'])} символов")
            return output

        except Exception as e:
            logger.error(f"Ошибка транскрипции: {e}")
            raise RuntimeError(f"Ошибка транскрипции: {e}") from e

    def _get_audio_duration(self, audio_path: str) -> float:
        """Получить длительность аудио файла в секундах."""
        import soundfile as sf
        try:
            with sf.SoundFile(audio_path) as f:
                return f.frames / f.samplerate
        except Exception:
            return 0.0

    def _parse_segments(self, segments: List[Dict]) -> List[Dict]:
        """Парсинг сегментов из результата транскрипции."""
        parsed = []
        for seg in segments:
            parsed.append({
                'start': seg.get('start', 0),
                'end': seg.get('end', 0),
                'text': seg.get('text', ''),
                'words': seg.get('words', [])
            })
        return parsed

    def batch_transcribe(
        self,
        audio_paths: List[str],
        language: str = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Транскрибировать несколько аудио файлов.

        Args:
            audio_paths: Список путей к аудио файлам
            language: Язык для всех файлов
            **kwargs: Дополнительные параметры для transcribe()

        Returns:
            Список результатов транскрипции
        """
        results = []
        for i, audio_path in enumerate(audio_paths):
            logger.info(f"Транскрипция [{i + 1}/{len(audio_paths)}]: {audio_path}")
            try:
                result = self.transcribe(audio_path, language, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Ошибка для {audio_path}: {e}")
                results.append({'error': str(e)})
        return results


def transcribe_audio(
    audio_path: str,
    model_path: str = None,
    language: str = None,
    device: str = None
) -> Dict[str, Any]:
    """
    Упрощенная функция транскрипции.

    Args:
        audio_path: Путь к аудио файлу
        model_path: Путь к модели (опционально)
        language: Язык (опционально)
        device: Устройство (опционально)

    Returns:
        Результат транскрипции
    """
    processor = QwenASRProcessor(model_path=model_path, device=device)
    return processor.transcribe(audio_path, language=language)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python asr.py <audio_path> [language]")
        sys.exit(1)

    audio_file = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        processor = QwenASRProcessor()
        result = processor.transcribe(audio_file, language=language)

        print(f"\n{'='*60}")
        print(f"Язык: {result['language']}")
        print(f"Длительность: {result['duration']:.2f} сек")
        print(f"{'='*60}")
        print(f"\nТекст:\n{result['text']}")
        print(f"\n{'='*60}")
        print(f"Символов: {len(result['text'])}")
        print(f"Слов: {len(result['text'].split())}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
