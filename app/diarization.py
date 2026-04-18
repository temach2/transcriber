"""
Diarization Module
Uses pyannote.audio 3.1 for speaker diarization (speaker separation).
All processing is offline with local models.
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import torch
import numpy as np
from loguru import logger

# Установка офлайн-режима Hugging Face ДО импорта любых библиотек
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    logger.warning("pyannote.audio не установлен, использование fallback режима")
    PYANNOTE_AVAILABLE = False
    Pipeline = None

# Допустимые настройки диаризации
DEFAULT_NUM_SPEAKERS = 2
MIN_NUM_SPEAKERS = 1
MAX_NUM_SPEAKERS = 10

logger.info("Diarization module initialized in OFFLINE mode")


class SpeakerDiarization:
    """Обработчик диаризации спикеров с использованием локальной модели pyannote."""

    def __init__(
        self,
        model_path: str = None,
        device: str = None,
        num_speakers: int = None,
        min_speakers: int = MIN_NUM_SPEAKERS,
        max_speakers: int = MAX_NUM_SPEAKERS,
        local_files_only: bool = True
    ):
        """
        Инициализация диаризатора.

        Args:
            model_path: Путь к локальной модели (по умолчанию ./models/pyannote-speaker-diarization-3.1)
            device: Устройство для inference ('cuda' или 'cpu')
            num_speakers: Количество спикеров (None = автоопределение)
            min_speakers: Минимальное количество спикеров
            max_speakers: Максимальное количество спикеров
            local_files_only: Использовать только локальные файлы
        """
        # Определение пути к модели
        self.model_path = model_path
        if self.model_path is None:
            self.model_path = os.path.join(
                os.path.dirname(__file__), '..', 'models', 'pyannote-speaker-diarization-3.1'
            )
        self.model_path = os.path.abspath(self.model_path)

        # Определение устройства
        self.device = device
        if self.device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Настройки количества спикеров
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers

        # Модель
        self.pipeline = None
        self.local_files_only = local_files_only

        # Инициализация
        self._initialize_pipeline()

        logger.info(f"SpeakerDiarization initialized: device={self.device}, num_speakers={num_speakers}")

    def _initialize_pipeline(self) -> bool:
        """
        Инициализация пайплайна pyannote.

        Returns:
            True если пайплайн успешно загружен, иначе False
        """
        if not PYANNOTE_AVAILABLE:
            logger.error("Библиотека pyannote.audio не установлена")
            return False

        try:
            logger.info(f"Загрузка модели диаризации из: {self.model_path}")

            # Проверка существования модели
            if not os.path.exists(self.model_path):
                logger.error(f"Модель не найдена: {self.model_path}")
                return False

            # Загрузка пайплайна
            self.pipeline = Pipeline.from_pretrained(
                self.model_path,
                device=torch.device(self.device),
                local_files_only=self.local_files_only
            )

            logger.info("Модель pyannote speaker-diarization 3.1 успешно загружена")
            return True

        except Exception as e:
            logger.error(f"Ошибка загрузки модели диаризации: {e}")
            self.pipeline = None
            return False

    def diarize(
        self,
        audio_path: str,
        num_speakers: int = None,
        min_speakers: int = None,
        max_speakers: int = None
    ) -> List[Dict[str, Any]]:
        """
        Выполнить диаризацию спикеров.

        Args:
            audio_path: Путь к аудио файлу (WAV 16kHz рекомендуется)
            num_speakers: Количество спикеров (переопределяет инициализацию)
            min_speakers: Минимальное количество спикеров
            max_speakers: Максимальное количество спикеров

        Returns:
            Список сегментов с информацией о спикерах:
            [
                {
                    'start': float,    # Начало сегмента в секундах
                    'end': float,      # Конец сегмента в секундах
                    'speaker': str,    # Идентификатор спикера (SPEAKER_01, SPEAKER_02, ...)
                    'duration': float  # Длительность сегмента
                },
                ...
            ]
        """
        if self.pipeline is None:
            raise RuntimeError("Пайплайн диаризации не инициализирован.")

        # Параметры
        n_speakers = num_speakers if num_speakers is not None else self.num_speakers
        min_spk = min_speakers if min_speakers is not None else self.min_speakers
        max_spk = max_speakers if max_speakers is not None else self.max_speakers

        try:
            # Выполнение диаризации
            diarization = self.pipeline(
                audio_path,
                num_speakers=n_speakers,
                min_speakers=min_spk,
                max_speakers=max_spk
            )

            # Парсинг результатов
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segment = {
                    'start': float(turn.start),
                    'end': float(turn.end),
                    'speaker': speaker,
                    'duration': float(turn.end - turn.start)
                }
                segments.append(segment)

            # Сортировка по времени начала
            segments.sort(key=lambda x: x['start'])

            logger.info(f"Диаризация завершена: {len(segments)} сегментов, "
                       f"{len(set(s['speaker'] for s in segments))} уникальных спикеров")

            return segments

        except Exception as e:
            logger.error(f"Ошибка диаризации: {e}")
            raise RuntimeError(f"Ошибка диаризации: {e}") from e

    def get_speaker_count(self, audio_path: str) -> int:
        """
        Получить количество уникальных спикеров в аудио.

        Args:
            audio_path: Путь к аудио файлу

        Returns:
            Количество уникальных спикеров
        """
        segments = self.diarize(audio_path)
        speakers = set(s['speaker'] for s in segments)
        return len(speakers)

    def export_segments(
        self,
        segments: List[Dict],
        output_path: str,
        format: str = 'rttm'
    ) -> str:
        """
        Экспортировать сегменты в файл.

        Args:
            segments: Список сегментов
            output_path: Путь к выходному файлу
            format: Формат вывода ('rttm', 'json', 'csv')

        Returns:
            Путь к созданному файлу
        """
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        if format == 'rttm':
            return self._export_rttm(segments, output_path)
        elif format == 'json':
            return self._export_json(segments, output_path)
        elif format == 'csv':
            return self._export_csv(segments, output_path)
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")

    def _export_rttm(self, segments: List[Dict], output_path: str) -> str:
        """Экспорт в RTTM формат."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for seg in segments:
                f.write(
                    f"SPEAKER {seg['speaker']} {seg['start']:.3f} "
                    f"{seg['duration']:.3f} <NA> <NA> <NA> <NA>\n"
                )
        return output_path

    def _export_json(self, segments: List[Dict], output_path: str) -> str:
        """Экспорт в JSON формат."""
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, indent=2, ensure_ascii=False)
        return output_path

    def _export_csv(self, segments: List[Dict], output_path: str) -> str:
        """Экспорт в CSV формат."""
        import csv
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start', 'end', 'speaker', 'duration'])
            for seg in segments:
                writer.writerow([seg['start'], seg['end'], seg['speaker'], seg['duration']])
        return output_path


def diarize_audio(
    audio_path: str,
    model_path: str = None,
    num_speakers: int = None,
    device: str = None
) -> List[Dict[str, Any]]:
    """
    Упрощенная функция диаризации.

    Args:
        audio_path: Путь к аудио файлу
        model_path: Путь к модели (опционально)
        num_speakers: Количество спикеров (опционально)
        device: Устройство (опционально)

    Returns:
        Список сегментов
    """
    diarizer = SpeakerDiarization(model_path=model_path, device=device, num_speakers=num_speakers)
    return diarizer.diarize(audio_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python diarization.py <audio_path> [num_speakers]")
        sys.exit(1)

    audio_file = sys.argv[1]
    num_speakers = int(sys.argv[2]) if len(sys.argv) > 2 else None

    try:
        diarizer = SpeakerDiarization()
        segments = diarizer.diarize(audio_file, num_speakers=num_speakers)

        print(f"\n{'='*60}")
        print(f"Диаризация завершена: {len(segments)} сегментов")
        print(f"{'='*60}\n")

        # Вывод уникальных спикеров
        speakers = set(s['speaker'] for s in segments)
        print(f"Найдено спикеров: {len(speakers)}")
        for speaker in sorted(speakers):
            speaker_segments = [s for s in segments if s['speaker'] == speaker]
            total_duration = sum(s['duration'] for s in speaker_segments)
            print(f"  {speaker}: {len(speaker_segments)} сегментов, {total_duration:.2f} сек")

        print(f"\n{'='*60}")
        print("Сегменты:")
        print(f"{'-'*60}")
        for seg in segments[:10]:  # Показать первые 10
            print(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['speaker']} "
                  f"({seg['duration']:.2f}s)")
        if len(segments) > 10:
            print(f"... и еще {len(segments) - 10} сегментов")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
