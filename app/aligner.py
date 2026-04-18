"""
Forced Alignment Module
Uses Qwen3-ForcedAligner-0.6B for word-level timestamp alignment.
All processing is offline with local models.
"""

import os
from typing import Dict, List, Optional, Tuple, Any

import torch
from loguru import logger

# Установка офлайн-режима Hugging Face ДО импорта
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

try:
    from qwen_asr import Qwen3ForcedAligner
    ALIGNER_AVAILABLE = True
except ImportError:
    logger.warning("Qwen3ForcedAligner не установлен, использование fallback режима")
    ALIGNER_AVAILABLE = False
    Qwen3ForcedAligner = None

logger.info("Forced Alignment module initialized in OFFLINE mode")


class ForcedAligner:
    """Обработчик выравнивания с использованием локальной модели Qwen3-ForcedAligner-0.6B."""

    def __init__(
        self,
        model_path: str = None,
        device: str = None,
        local_files_only: bool = True
    ):
        """
        Инициализация выравнивателя.

        Args:
            model_path: Путь к локальной модели (по умолчанию ./models/Qwen3-ForcedAligner-0.6B)
            device: Устройство для inference ('cuda' или 'cpu')
            local_files_only: Использовать только локальные файлы
        """
        # Определение пути к модели
        self.model_path = model_path
        if self.model_path is None:
            self.model_path = os.path.join(
                os.path.dirname(__file__), '..', 'models', 'Qwen3-ForcedAligner-0.6B'
            )
        self.model_path = os.path.abspath(self.model_path)

        # Определение устройства
        self.device = device
        if self.device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Модель
        self.aligner = None
        self.local_files_only = local_files_only

        # Инициализация
        self._initialize_aligner()

        logger.info(f"ForcedAligner initialized: device={self.device}")

    def _initialize_aligner(self) -> bool:
        """
        Инициализация модели Forced Aligner.

        Returns:
            True если модель успешно загружена, иначе False
        """
        if not ALIGNER_AVAILABLE:
            logger.warning("Библиотека qwen_asr с ForcedAligner не установлена")
            logger.info("Используется fallback режим - временные метки будут получены из ASR")
            return False

        try:
            logger.info(f"Загрузка модели выравнивания из: {self.model_path}")

            # Проверка существования модели
            if not os.path.exists(self.model_path):
                logger.warning(f"Модель не найдена: {self.model_path}")
                logger.info("Используется fallback режим")
                return False

            # Загрузка модели
            self.aligner = Qwen3ForcedAligner.from_pretrained(
                self.model_path,
                device_map=self.device,
                local_files_only=self.local_files_only
            )

            logger.info("Модель Qwen3-ForcedAligner-0.6B успешно загружена")
            return True

        except Exception as e:
            logger.warning(f"Ошибка загрузки модели выравнивания: {e}")
            logger.info("Используется fallback режим")
            self.aligner = None
            return False

    def align(
        self,
        audio_path: str,
        text: str,
        language: str = None
    ) -> List[Dict[str, Any]]:
        """
        Выполнитьforced alignment для получения word-level таймкодов.

        Args:
            audio_path: Путь к аудио файлу
            text: Текст для выравнивания
            language: Язык (опционально)

        Returns:
            Список слов с таймкодами:
            [
                {
                    'word': str,
                    'start': float,  # Начало слова в секундах
                    'end': float,    # Конец слова в секундах
                    'confidence': float  # Уверенность (опционально)
                },
                ...
            ]
        """
        if self.aligner is None:
            # Fallback: вернуть пустой список
            logger.info("ForcedAligner не инициализирован, возвращаем пустой список")
            return []

        try:
            # Выполнение выравнивания
            result = self.aligner.align(
                audio_path,
                text,
                language=language or 'ru'
            )

            # Парсинг результатов
            word_timestamps = []
            for word_info in result.get('words', []):
                word_timestamps.append({
                    'word': word_info.get('word', ''),
                    'start': float(word_info.get('start', 0)),
                    'end': float(word_info.get('end', 0)),
                    'confidence': float(word_info.get('confidence', 1.0))
                })

            logger.info(f"Выравнивание завершено: {len(word_timestamps)} слов")

            return word_timestamps

        except Exception as e:
            logger.error(f"Ошибка выравнивания: {e}")
            # Fallback: вернуть пустой список
            return []

    def align_segments(
        self,
        audio_path: str,
        segments: List[Dict[str, Any]],
        language: str = None
    ) -> List[Dict[str, Any]]:
        """
        Выполнить выравнивание для сегментов диаризации.

        Args:
            audio_path: Путь к аудио файлу
            segments: Список сегментов диаризации
            language: Язык

        Returns:
            Список сегментов с добавленными word-level таймкодами
        """
        result_segments = []

        for seg in segments:
            segment_text = seg.get('text', '')
            if segment_text:
                word_timestamps = self.align(audio_path, segment_text, language)
                seg['words'] = word_timestamps
            result_segments.append(seg)

        return result_segments


def align_audio_text(
    audio_path: str,
    text: str,
    model_path: str = None,
    device: str = None
) -> List[Dict[str, Any]]:
    """
    Упрощенная функция выравнивания.

    Args:
        audio_path: Путь к аудио файлу
        text: Текст для выравнивания
        model_path: Путь к модели (опционально)
        device: Устройство (опционально)

    Returns:
        Список слов с таймкодами
    """
    aligner = ForcedAligner(model_path=model_path, device=device)
    return aligner.align(audio_path, text)


def merge_segments_with_alignment(
    diarization_segments: List[Dict],
    word_timestamps: List[Dict],
    tolerance: float = 0.1
) -> List[Dict]:
    """
    Объединить сегменты диаризации с word-level таймкодами.

    Args:
        diarization_segments: Сегменты от диаризатора
        word_timestamps: Слова с таймкодами от aligner
        tolerance: Толеранс для привязки слов к сегментам

    Returns:
        Сегменты с объединенным текстом
    """
    dialogue = []

    for seg in diarization_segments:
        seg_start = seg['start']
        seg_end = seg['end']
        speaker = seg['speaker']

        # Найти слова, попадающие в этот сегмент
        seg_words = []
        for word_info in word_timestamps:
            word_start = word_info['start']
            word_end = word_info['end']

            # Проверка пересечения
            if (word_end >= seg_start - tolerance and
                word_start <= seg_end + tolerance):
                seg_words.append(word_info)

        # Сформировать текст
        text = ' '.join(w['word'] for w in seg_words)

        dialogue.append({
            'speaker': speaker,
            'text': text,
            'start': seg_start,
            'end': seg_end,
            'words': seg_words
        })

    return dialogue


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Использование: python aligner.py <audio_path> <text>")
        sys.exit(1)

    audio_file = sys.argv[1]
    text = sys.argv[2]

    try:
        aligner = ForcedAligner()

        # Если не загрузился, показать предупреждение
        if not hasattr(aligner, 'aligner') or aligner.aligner is None:
            print("Предупреждение: ForcedAligner не инициализирован")
            print("Попытка использовать ASR для получения временных меток...")

        word_timestamps = aligner.align(audio_file, text)

        print(f"\n{'='*60}")
        print(f"Выравнивание: {len(word_timestamps)} слов")
        print(f"{'='*60}\n")

        for w in word_timestamps[:15]:
            print(f"[{w['start']:.2f}s - {w['end']:.2f}s] {w['word']}")

        if len(word_timestamps) > 15:
            print(f"... и еще {len(word_timestamps) - 15} слов")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
