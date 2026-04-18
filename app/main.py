"""
Gradio Web UI for Qwen Medical Transcriber
Provides web interface for audio transcription with speaker diarization.
"""

import os
import gradio as gr
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from loguru import logger

# Установка офлайн-режима Hugging Face
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

from processor import MedicalAudioProcessor
from audio_converter import AudioConverter

logger.info("Gradio Web UI initialized in OFFLINE mode")


# Глобальные переменные
processor: Optional[MedicalAudioProcessor] = None
config: Dict[str, Any] = {}


def init_processor():
    """Инициализировать процессор (ленивая инициализация)."""
    global processor
    if processor is None:
        logger.info("Инициализация MedicalAudioProcessor...")
        processor = MedicalAudioProcessor()
    return processor


def transcribe_audio(
    audio_file,
    language: str,
    num_speakers: int,
    use_alignment: bool,
    include_timestamps: bool,
    progress=gr.Progress()
) -> tuple:
    """
    Обработать загруженный аудио файл.

    Args:
        audio_file: Загруженный файл (Gradio File)
        language: Язык
        num_speakers: Количество спикеров
        use_alignment: Использовать ли forced alignment
        include_timestamps: Включать ли таймкоды
        progress: Gradio progress tracker

    Returns:
        Кортеж (output_doc, status, dialogue_text)
    """
    if audio_file is None:
        return None, "Ошибка: Не выбран файл для обработки", ""

    try:
        # Получить путь к файлу
        input_path = audio_file.name

        # Инициализация процессора
        processor = init_processor()

        # Callback для отображения прогресса
        def progress_callback(message, progress_val):
            progress(message)
            logger.info(f"Прогресс: {message}")

        # Обновить callback
        processor.progress_callback = progress_callback

        # Запуск обработки
        result = processor.process_file(
            input_path=input_path,
            language=language if language != 'auto' else None,
            num_speakers=num_speakers if num_speakers > 0 else None,
            use_alignment=use_alignment
        )

        if result['success']:
            output_doc = result['output_path']
            status = f"✅ Успех! Документ создан: {output_doc}"
            status += f"\n🕒 Длительность: {result['duration']:.1f} сек"
            status += f"\n👥 Спикеров: {len(set(s['speaker'] for s in result['dialogue']))}"
            status += f"\n📝 Сегментов: {len(result['dialogue'])}"

            # Формирование текста диалога для предпросмотра
            dialogue_text = format_dialogue(result['dialogue'])
        else:
            output_doc = None
            status = f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}"
            dialogue_text = ""

        return output_doc, status, dialogue_text

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None, f"❌ Критическая ошибка: {str(e)}", ""


def format_dialogue(dialogue: List[Dict]) -> str:
    """Форматировать диалог в читаемый текст."""
    lines = []
    for seg in dialogue:
        speaker = seg.get('speaker', 'Unknown')
        text = seg.get('text', '')

        # Маппинг спикеров
        if 'SPEAKER_00' in speaker or 'SPEAKER_01' in speaker:
            role_map = {
                'SPEAKER_00': 'Врач',
                'SPEAKER_01': 'Пациент',
            }
            speaker = role_map.get(speaker, speaker)

        lines.append(f"{speaker}: {text}")

    return "\n".join(lines)


def process_example_audio(
    progress=gr.Progress()
) -> tuple:
    """Обработать пример аудио (заглушка для демонстрации)."""
    # Здесь можно добавить путь к примеру
    # Для демо используем пустой результат
    progress("Демонстрация...")
    return None, "⚠️ Для демонстрации загрузите аудио файл", ""


def create_interface() -> gr.Blocks:
    """Создать интерфейс Gradio."""

    # Описание
    DESCRIPTION = """
    <div style='text-align: center'>
        <h1>🏥 Qwen Medical Transcriber</h1>
        <p>Профессиональная система транскрибации медицинских консультаций</p>
        <p style='color: #666; font-size: 0.9em;'>
            • Полностью офлайн-работа<br>
            • Локальные модели (Qwen3-ASR, PyAnnote, ForcedAligner)<br>
            • Разделение диалога по ролям Врач/Пациент<br>
            • Генерация Word-документа
        </p>
    </div>
    """

    # CSS стили
    CSS = """
    .gradio-container {
        max-width: 900px !important;
        margin: auto !important;
        padding: 20px !important;
    }
    .status-box {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background: #f9f9f9;
    }
    .dialogue-box {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background: #fafafa;
        max-height: 400px;
        overflow-y: auto;
    }
    .role-doctor {
        color: #1a237e;
        font-weight: bold;
    }
    .role-patient {
        margin-left: 20px;
        color: #333;
    }
    """

    with gr.Blocks(theme=gr.themes.Soft(), css=CSS) as demo:
        # Header
        gr.Markdown(DESCRIPTION)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📁 Входные данные")

                # Загрузка аудио
                audio_input = gr.File(
                    label="Аудио файл (WAV, MP3, FLAC, M4A, OGG)",
                    file_types=['audio'],
                    type='file'
                )

                # Выбор языка
                language_input = gr.Dropdown(
                    label="Язык",
                    choices=[
                        ('Автоматическое определение', 'auto'),
                        ('Русский', 'ru'),
                        ('Английский', 'en')
                    ],
                    value='ru'
                )

                # Количество спикеров
                speakers_input = gr.Slider(
                    label="Количество спикеров",
                    minimum=1,
                    maximum=10,
                    step=1,
                    value=2
                )

            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Настройки")

                # Forced alignment
                alignment_input = gr.Checkbox(
                    label="Forced Alignment (точные таймкоды)",
                    value=True,
                    info="Требует больше времени, но дает точные таймкоды на уровне слов"
                )

                # Таймкоды
                timestamps_input = gr.Checkbox(
                    label="Включать таймкоды",
                    value=True,
                    info="Добавить временные метки в документ"
                )

                # Кнопка запуска
                process_button = gr.Button(
                    "🚀 Обработать",
                    variant='primary',
                    size='lg'
                )

        # Output section
        gr.Markdown("### 📊 Результаты")

        with gr.Row():
            with gr.Column(scale=1):
                # Статус
                status_output = gr.Textbox(
                    label="Статус",
                    lines=4,
                    max_lines=10,
                    show_copy_button=True
                )

                # Выходной документ
                doc_output = gr.File(
                    label="Скачать DOCX",
                    file_types=['.docx']
                )

            with gr.Column(scale=1):
                # Предпросмотр диалога
                gr.Markdown("#### 🔍 Предпросмотр диалога")
                dialogue_output = gr.Textbox(
                    label="Диалог",
                    lines=20,
                    max_lines=30,
                    show_copy_button=True,
                    container=True,
                    scale=1
                )

        # Examples
        gr.Markdown("### 📚 Примеры")

        with gr.Accordion("Показать примеры использования", open=False):
            gr.Markdown("""
            **Рекомендации по аудио:**
            - Формат: WAV, MP3, FLAC, M4A, OGG
            - Частота: 16 kHz (рекомендуется)
            - Каналы: Mono
            - Длительность: до 60 минут

            **Настройки спикеров:**
            - 2 спикера: Врач и Пациент (по умолчанию)
            - 3+ спикеров: Для групповых консультаций

            **Время обработки:**
            - Короткое аудио (1-5 мин): 10-30 сек
            - Среднее аудио (5-15 мин): 30-60 сек
            - Длинное аудио (15+ мин): 60+ сек
            """)

        # Footer
        gr.Markdown("""
        <div style='text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd;'>
            <p style='color: #666;'>© 2026 Qwen Medical Transcriber | Офлайн система транскрибации</p>
            <p style='color: #999; font-size: 0.85em;'>
                Модели: Qwen3-ASR-1.7B, PyAnnote Speaker Diarization 3.1, Qwen3-ForcedAligner-0.6B
            </p>
        </div>
        """)

        # Events
        process_button.click(
            fn=transcribe_audio,
            inputs=[
                audio_input,
                language_input,
                speakers_input,
                alignment_input,
                timestamps_input
            ],
            outputs=[doc_output, status_output, dialogue_output],
            api_name="transcribe"
        )

    return demo


def launch_ui(
    host: str = None,
    port: int = None,
    share: bool = False,
    inbrowser: bool = False
):
    """
    Запустить Gradio интерфейс.

    Args:
        host: Хост (по умолчанию 0.0.0.0)
        port: Порт (по умолчанию 7860)
        share: Общать ли ссылку
        inbrowser: Открывать ли в браузере
    """
    if host is None:
        host = os.environ.get('GRADIO_HOST', '0.0.0.0')

    if port is None:
        port = int(os.environ.get('GRADIO_PORT', '7860'))

    if 'GRADIO_SHARE' in os.environ:
        share = os.environ.get('GRADIO_SHARE', 'false').lower() == 'true'

    # Настройка логгирования gradio
    import logging
    logging.getLogger("gradio").setLevel(logging.WARNING)

    # Создание и запуск интерфейса
    interface = create_interface()
    interface.queue()

    print(f"\n{'='*60}")
    print(f"🚀 Qwen Medical Transcriber Web UI")
    print(f"{'='*60}")
    print(f".URL: http://{host}:{port}")
    print(f"Port: {port}")
    print(f"Share: {share}")
    print(f"{'='*60}\n")

    interface.launch(
        server_name=host,
        server_port=port,
        share=share,
        inbrowser=inbrowser,
        quiet=True
    )


if __name__ == "__main__":
    # Запуск веб-интерфейса
    launch_ui()
