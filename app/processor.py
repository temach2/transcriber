"""
Processor Module
Orchestrates the complete audio processing pipeline.
Coordinates audio conversion, diarization, ASR, alignment, and document generation.
"""

import os
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from datetime import datetime
from loguru import logger

# Установка офлайн-режима Hugging Face
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

from audio_converter import AudioConverter
from diarization import SpeakerDiarization
from asr import QwenASRProcessor
from aligner import ForcedAligner
from docx_generator import MedicalDialogueDocGenerator

logger.info("Processor module initialized in OFFLINE mode")


class MedicalAudioProcessor:
    """
    Оркестратор обработки медицинского аудио.
    Выполняет полный пайплайн: конвертация -> диаризация -> ASR -> align -> DOCX
    """

    # Пути по умолчанию
    DEFAULT_CONFIG = {
        'models_dir': './models',
        'output_dir': './output',
        'uploads_dir': './uploads',
        'converted_dir': './uploads/converted',
        'logs_dir': './logs',
        'target_sample_rate': 16000,
        'target_channels': 1,
        'target_rms_db': -20,
        'default_language': 'ru',
        'default_num_speakers': 2,
        'min_speakers': 1,
        'max_speakers': 5,
        'include_timestamps': True,
        'include_speaker_labels': True,
    }

    def __init__(
        self,
        config: Dict = None,
        progress_callback: Callable = None,
        device: str = None
    ):
        """
        Инициализация процессора.

        Args:
            config: Конфигурация (опционально)
            progress_callback: Callback для отслеживания прогресса
            device: Устройство для inference ('cuda' или 'cpu')
        """
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.progress_callback = progress_callback
        self.device = device or ('cuda' if __import__('torch').cuda.is_available() else 'cpu')

        # Компоненты
        self.audio_converter = None
        self.diarization = None
        self.asr = None
        self.aligner = None
        self.docx_generator = None

        # Метаданные последней обработки
        self.last_metadata = {}
        self.last_dialogue = []

        # Инициализация компонентов
        self._init_components()

        logger.info(f"MedicalAudioProcessor initialized: device={self.device}")

    def _init_components(self):
        """Инициализировать все компоненты."""
        # Audio Converter
        self.audio_converter = AudioConverter(
            target_sample_rate=self.config['target_sample_rate'],
            target_channels=self.config['target_channels'],
            target_rms_db=self.config['target_rms_db']
        )

        # Diarization
        self.diarization = SpeakerDiarization(
            num_speakers=self.config['default_num_speakers'],
            min_speakers=self.config['min_speakers'],
            max_speakers=self.config['max_speakers'],
            device=self.device
        )

        # ASR
        self.asr = QwenASRProcessor(
            device=self.device,
            local_files_only=True
        )

        # Aligner (опционально)
        self.aligner = ForcedAligner(
            device=self.device,
            local_files_only=True
        )

        # DocX Generator
        speaker_map = {
            'SPEAKER_00': 'Врач',
            'SPEAKER_01': 'Пациент',
        }
        self.docx_generator = MedicalDialogueDocGenerator(
            speaker_map=speaker_map
        )

    def _update_progress(self, message: str, progress: float = None):
        """Отправить обновление прогресса."""
        if self.progress_callback:
            self.progress_callback(message, progress)

    def process_file(
        self,
        input_path: str,
        output_path: str = None,
        language: str = None,
        num_speakers: int = None,
        use_alignment: bool = True
    ) -> Dict[str, Any]:
        """
        Обработать аудио файл и сгенерировать DOCX.

        Args:
            input_path: Путь к входному аудио файлу
            output_path: Путь к выходному DOCX файлу
            language: Язык ('ru', 'en' или 'auto')
            num_speakers: Количество спикеров
            use_alignment: Использовать ли forced alignment

        Returns:
            Словарь с результатами:
            {
                'success': bool,
                'output_path': str,
                'metadata': dict,
                'dialogue': list,
                'duration': float,
                'error': str (если ошибка)
            }
        """
        start_time = time.time()
        result = {
            'success': False,
            'output_path': None,
            'metadata': {},
            'dialogue': [],
            'duration': 0,
            'error': None
        }

        try:
            # Определение путей
            input_path = os.path.abspath(input_path)
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Файл не найден: {input_path}")

            output_path = output_path or os.path.join(
                self.config['output_dir'],
                Path(input_path).stem + '.docx'
            )
            output_path = os.path.abspath(output_path)

            # Шаг 1: Конвертация аудио
            self._update_progress("Конвертация аудио...", 10)
            converted_path, audio_duration = self._convert_audio(input_path)

            # Шаг 2: Диаризация
            self._update_progress("Разделение спикеров...", 25)
            diarization_segments = self._perform_diarization(
                converted_path,
                num_speakers
            )

            # Шаг 3: ASR для каждого сегмента
            self._update_progress("Транскрипция...", 40)
            asr_results = self._perform_asr(converted_path, language)

            # Шаг 4: Forced Alignment (опционально)
            if use_alignment:
                self._update_progress("Выравнивание таймкодов...", 60)
                word_timestamps = self._perform_alignment(
                    converted_path,
                    asr_results.get('text', '')
                )
            else:
                word_timestamps = []

            # Шаг 5: Объединение результатов
            self._update_progress("Формирование диалога...", 80)
            dialogue = self._merge_results(
                diarization_segments,
                asr_results,
                word_timestamps
            )

            # Шаг 6: Генерация документа
            self._update_progress("Генерация документа...", 90)
            doc = self._generate_document(dialogue, audio_duration)

            # Шаг 7: Сохранение
            self.docx_generator.save(doc, output_path)

            # Заполнение результата
            result['success'] = True
            result['output_path'] = output_path
            result['metadata'] = self.last_metadata
            result['dialogue'] = dialogue
            result['duration'] = audio_duration

            self.last_dialogue = dialogue

        except Exception as e:
            logger.error(f"Ошибка обработки: {e}")
            result['error'] = str(e)
            if self.progress_callback:
                self.progress_callback(f"Ошибка: {e}", -1)

        # Расчет времени
        result['duration'] = time.time() - start_time
        self._update_progress(f"Готово! ({result['duration']:.1f} сек)", 100)

        logger.info(f"Обработка завершена: {result['success']}")
        return result

    def _convert_audio(self, input_path: str) -> tuple:
        """Конвертировать аудио в WAV 16kHz."""
        converted_dir = self.config['converted_dir']
        os.makedirs(converted_dir, exist_ok=True)

        output_filename = Path(input_path).stem + '.wav'
        output_path = os.path.join(converted_dir, output_filename)

        def progress_callback(message, progress=None):
            self._update_progress(message, progress)

        output_path, duration = self.audio_converter.convert_with_cache(
            input_path,
            converted_dir,
            progress_callback=progress_callback
        )

        self.last_metadata['audio_duration'] = duration
        self.last_metadata['original_file'] = input_path
        self.last_metadata['converted_file'] = output_path

        return output_path, duration

    def _perform_diarization(self, audio_path: str, num_speakers: int = None) -> list:
        """Выполнить диаризацию спикеров."""
        if num_speakers is None:
            num_speakers = self.config['default_num_speakers']

        segments = self.diarization.diarize(
            audio_path,
            num_speakers=num_speakers,
            min_speakers=self.config['min_speakers'],
            max_speakers=self.config['max_speakers']
        )

        self.last_metadata['num_speakers'] = len(set(s['speaker'] for s in segments))
        self.last_metadata['num_segments'] = len(segments)

        return segments

    def _perform_asr(self, audio_path: str, language: str = None) -> dict:
        """Выполнить ASR транскрипцию."""
        if language is None:
            language = self.config['default_language']

        result = self.asr.transcribe(
            audio_path,
            language=language,
            return_timestamps=True
        )

        self.last_metadata['language'] = result.get('language', 'unknown')
        self.last_metadata['asr_text_length'] = len(result.get('text', ''))

        return result

    def _perform_alignment(self, audio_path: str, text: str) -> list:
        """Выполнить forced alignment."""
        word_timestamps = self.aligner.align(
            audio_path,
            text,
            language=self.config['default_language']
        )
        return word_timestamps

    def _merge_results(
        self,
        diarization_segments: list,
        asr_results: dict,
        word_timestamps: list
    ) -> list:
        """Объединить результаты диаризации и ASR."""
        dialogue = []

        # Если есть word-level таймкоды, используем их для более точного разделения
        if word_timestamps:
            # Группируем слова по сегментам
            for seg in diarization_segments:
                seg_start = seg['start']
                seg_end = seg['end']

                seg_words = []
                for word_info in word_timestamps:
                    if (word_info['start'] >= seg_start - 0.5 and
                        word_info['end'] <= seg_end + 0.5):
                        seg_words.append(word_info)

                text = ' '.join(w['word'] for w in seg_words)
                dialogue.append({
                    'speaker': seg['speaker'],
                    'text': text,
                    'start': seg['start'],
                    'end': seg['end'],
                    'words': seg_words
                })
        else:
            # Fallback: просто используем сегменты диаризации с текстом ASR
            asr_text = asr_results.get('text', '')
            segments = asr_results.get('segments', [])

            for seg in diarization_segments:
                # Найти соответствующий текст из ASR
                seg_start = seg['start']
                seg_end = seg['end']

                # Извлечь текст для этого сегмента из ASR segments
                seg_text = ''
                for asr_seg in segments:
                    if (asr_seg.get('end', 0) >= seg_start and
                        asr_seg.get('start', 0) <= seg_end):
                        seg_text += asr_seg.get('text', '') + ' '

                dialogue.append({
                    'speaker': seg['speaker'],
                    'text': seg_text.strip(),
                    'start': seg_start,
                    'end': seg_end
                })

        return dialogue

    def _generate_document(self, dialogue: list, duration: float) -> object:
        """Сгенерировать Word документ."""
        # Метаданные
        metadata = {
            'date': datetime.now().strftime('%d.%m.%Y'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'duration': f"{int(duration // 60)}:{int(duration % 60):02d}",
            **self.last_metadata
        }

        doc = self.docx_generator.generate(
            dialogue,
            metadata=metadata,
            include_timestamps=self.config['include_timestamps'],
            include_speaker_labels=self.config['include_speaker_labels']
        )

        return doc

    def process_batch(
        self,
        input_paths: List[str],
        output_dir: str = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Обработать несколько файлов.

        Args:
            input_paths: Список путей к файлам
            output_dir: Директория для выходных файлов
            **kwargs: Дополнительные параметры для process_file

        Returns:
            Список результатов обработки
        """
        results = []
        output_dir = output_dir or self.config['output_dir']
        os.makedirs(output_dir, exist_ok=True)

        for i, input_path in enumerate(input_paths):
            self._update_progress(
                f"Обработка [{i + 1}/{len(input_paths)}]: {Path(input_path).name}",
                10 + (i * 80 / len(input_paths))
            )

            # Генерация пути к выходному файлу
            output_filename = Path(input_path).stem + '.docx'
            output_path = os.path.join(output_dir, output_filename)

            result = self.process_file(input_path, output_path, **kwargs)
            results.append(result)

        self._update_progress("Готово!", 100)
        return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python processor.py <audio_file> [output.docx]")
        sys.exit(1)

    audio_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Callback для прогресса
    def progress_callback(message, progress):
        status = f"{message}"
        if progress is not None:
            status += f" ({progress:.0f}%)"
        print(status)

    processor = MedicalAudioProcessor(progress_callback=progress_callback)

    try:
        result = processor.process_file(audio_file, output_file)

        if result['success']:
            print(f"\n{'='*60}")
            print(f"Успех! Документ сохранен: {result['output_path']}")
            print(f"{'='*60}")
            print(f"Длительность: {result['duration']:.1f} сек")
            print(f"Сегментов: {len(result['dialogue'])}")
            print(f"Метаданные: {result['metadata']}")
        else:
            print(f"Ошибка: {result['error']}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
