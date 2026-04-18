"""
Settings Window Module
Settings configuration window for Windows desktop GUI.
"""

import os
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any, Optional

from loguru import logger


class SettingsWindow(ctk.CTkToplevel):
    """Окно настроек приложения."""

    def __init__(self, parent: ctk.CTk):
        """Инициализация окна настроек."""
        super().__init__(parent)
        self.title("Настройки")
        self.geometry("500x600")
        self.resizable(False, False)

        # Центрирование
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 250
        y = (self.winfo_screenheight() // 2) - 300
        self.geometry(f'500x600+{x}+{y}')

        # Принудительный фокус
        self.transient(parent)
        self.grab_set()

        # Переменные
        self.settings: Dict[str, Any] = {}

        # Создание интерфейса
        self._create_layout()

        # Загрузка текущих настроек
        self._load_settings()

        logger.info("Settings Window created")

    def _create_layout(self):
        """Создать макет окна."""
        # Создать canvas для прокрутки
        canvas = ctk.CTkCanvas(self, bg="#f8fafc", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        # Frame для содержимого
        self.content_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Привязка прокрутки
        self.content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Создать секции
        self._create_general_section()
        self._create_audio_section()
        self._create_output_section()
        self._create_models_section()

        # Кнопки
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Сохранить",
            command=self._save_all_settings,
            width=120
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.destroy,
            width=120
        )
        cancel_btn.pack(side="left", padx=5)

    def _create_general_section(self):
        """Создать секцию общих настроек."""
        frame = self._create_section_frame("Общие настройки")

        # Язык по умолчанию
        ctk.CTkLabel(frame, text="Язык по умолчанию:").pack(anchor="w", padx=10, pady=5)
        self.lang_var = ctk.StringVar(value="ru")
        lang_frame = ctk.CTkFrame(frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(lang_frame, text="Русский", variable=self.lang_var, value="ru").pack(side="left", padx=5)
        ctk.CTkRadioButton(lang_frame, text="Английский", variable=self.lang_var, value="en").pack(side="left", padx=5)
        ctk.CTkRadioButton(lang_frame, text="Автоматическое", variable=self.lang_var, value="auto").pack(side="left", padx=5)

        # Тема
        ctk.CTkLabel(frame, text="Тема интерфейса:").pack(anchor="w", padx=10, pady=5)
        self.theme_var = ctk.StringVar(value="light")
        theme_frame = ctk.CTkFrame(frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(theme_frame, text="Светлая", variable=self.theme_var, value="light").pack(side="left", padx=5)
        ctk.CTkRadioButton(theme_frame, text="Темная", variable=self.theme_var, value="dark").pack(side="left", padx=5)
        ctk.CTkRadioButton(theme_frame, text="Системная", variable=self.theme_var, value="system").pack(side="left", padx=5)

    def _create_audio_section(self):
        """Создать секцию настроек аудио."""
        frame = self._create_section_frame("Настройки аудио")

        # Количество спикеров
        ctk.CTkLabel(frame, text="Количество спикеров (по умолчанию):").pack(anchor="w", padx=10, pady=5)
        self.speakers_var = ctk.StringVar(value="2")
        ctk.CTkEntry(frame, textvariable=self.speakers_var, width=80).pack(anchor="w", padx=10, pady=5)

        # Включить forced alignment
        ctk.CTkLabel(frame, text="Forced Alignment (точные таймкоды):").pack(anchor="w", padx=10, pady=5)
        self.alignment_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(frame, variable=self.alignment_var, text="Включено").pack(anchor="w", padx=10, pady=5)

        # Включить таймкоды
        ctk.CTkLabel(frame, text="Таймкоды в документе:").pack(anchor="w", padx=10, pady=5)
        self.timestamps_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(frame, variable=self.timestamps_var, text="Включено").pack(anchor="w", padx=10, pady=5)

    def _create_output_section(self):
        """Создать секцию настроек вывода."""
        frame = self._create_section_frame("Настройки вывода")

        # Директория вывода
        ctk.CTkLabel(frame, text="Директория для результатов:").pack(anchor="w", padx=10, pady=5)
        self.output_dir_var = ctk.StringVar(value="./output")
        ctk.CTkEntry(frame, textvariable=self.output_dir_var, width=300).pack(anchor="w", padx=10, pady=5)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=10, pady=5)

        browse_btn = ctk.CTkButton(
            btn_frame,
            text="Обзор",
            command=self._browse_output_dir,
            width=80
        )
        browse_btn.pack(side="left")

        # Формат вывода
        ctk.CTkLabel(frame, text="Формат вывода:").pack(anchor="w", padx=10, pady=5)
        self.format_var = ctk.StringVar(value="docx")
        ctk.CTkOptionMenu(
            frame,
            variable=self.format_var,
            values=["docx", "txt", "both"]
        ).pack(anchor="w", padx=10, pady=5)

    def _create_models_section(self):
        """Создать секцию настроек моделей."""
        frame = self._create_section_frame("Настройки моделей")

        # Директория моделей
        ctk.CTkLabel(frame, text="Директория моделей:").pack(anchor="w", padx=10, pady=5)
        self.models_dir_var = ctk.StringVar(value="./models")
        ctk.CTkEntry(frame, textvariable=self.models_dir_var, width=300).pack(anchor="w", padx=10, pady=5)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=10, pady=5)

        browse_btn = ctk.CTkButton(
            btn_frame,
            text="Обзор",
            command=self._browse_models_dir,
            width=80
        )
        browse_btn.pack(side="left")

        # Статус моделей
        self.models_status = ctk.CTkLabel(
            frame,
            text="Проверка моделей...",
            text_color="#64748b"
        )
        self.models_status.pack(anchor="w", padx=10, pady=5)

        # Проверка моделей
        check_btn = ctk.CTkButton(
            frame,
            text="Проверить модели",
            command=self._check_models,
            width=120
        )
        check_btn.pack(anchor="w", padx=10, pady=5)

    def _create_section_frame(self, title: str) -> ctk.CTkFrame:
        """Создать фрейм секции."""
        frame = ctk.CTkFrame(self.content_frame, corner_radius=8, border_width=1, border_color="#e2e8f0")
        frame.pack(fill="x", padx=20, pady=10)

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color="#1e293b"
        )
        title_label.pack(anchor="w", padx=10, pady=10)

        return frame

    def _browse_output_dir(self):
        """Выбрать директорию вывода."""
        directory = ctk.filedialog.askdirectory(
            title="Выберите директорию для результатов",
            initialdir=self.output_dir_var.get() if self.output_dir_var.get() != "./output" else "."
        )
        if directory:
            self.output_dir_var.set(directory)

    def _browse_models_dir(self):
        """Выбрать директорию моделей."""
        directory = ctk.filedialog.askdirectory(
            title="Выберите директорию моделей",
            initialdir=self.models_dir_var.get() if self.models_dir_var.get() != "./models" else "."
        )
        if directory:
            self.models_dir_var.set(directory)

    def _check_models(self):
        """Проверить наличие моделей."""
        import os
        from pathlib import Path

        models_dir = self.models_dir_var.get()
        required_models = [
            "Qwen3-ASR-1.7B",
            "Qwen3-ForcedAligner-0.6B",
            "pyannote-speaker-diarization-3.1"
        ]

        found = []
        missing = []

        for model in required_models:
            model_path = os.path.join(models_dir, model)
            if os.path.exists(model_path):
                found.append(model)
            else:
                missing.append(model)

        if missing:
            self.models_status.configure(
                text=f"❌ Не найдено: {', '.join(missing)}",
                text_color="#ef4444"
            )
        else:
            self.models_status.configure(
                text=f"✅ Все модели найдены ({len(found)})",
                text_color="#22c55e"
            )

    def _load_settings(self):
        """Загрузить текущие настройки."""
        settings_file = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        if os.path.exists(settings_file):
            try:
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # Применить настройки
                if 'language' in settings:
                    lang_map = {'ru': 'Русский', 'en': 'Английский', 'auto': 'Автоматическое'}
                    if lang_map.get(settings['language']) in ['Русский', 'Английский', 'Автоматическое']:
                        self.lang_var.set(lang_map[settings['language']])

                if 'num_speakers' in settings:
                    self.speakers_var.set(str(settings['num_speakers']))

                if 'use_alignment' in settings:
                    self.alignment_var.set(settings['use_alignment'])

                if 'include_timestamps' in settings:
                    self.timestamps_var.set(settings['include_timestamps'])

                if 'output_dir' in settings:
                    self.output_dir_var.set(settings['output_dir'])

                if 'models_dir' in settings:
                    self.models_dir_var.set(settings['models_dir'])

            except Exception as e:
                logger.error(f"Ошибка загрузки настроек: {e}")

    def _save_all_settings(self):
        """Сохранить все настройки."""
        settings = {
            'language': self.lang_var.get(),
            'num_speakers': int(self.speakers_var.get()),
            'use_alignment': self.alignment_var.get(),
            'include_timestamps': self.timestamps_var.get(),
            'output_dir': self.output_dir_var.get(),
            'models_dir': self.models_dir_var.get(),
            'theme': self.theme_var.get(),
            'format': self.format_var.get(),
        }

        settings_file = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        try:
            import json
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            # Применить тему
            if self.theme_var.get() == 'system':
                ctk.set_appearance_mode("system")
            elif self.theme_var.get() == 'dark':
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")

            messagebox.showinfo("Сохранено", "Настройки успешно сохранены")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
            logger.error(f"Ошибка сохранения настроек: {e}")


if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    settings = SettingsWindow(app)
    app.mainloop()
