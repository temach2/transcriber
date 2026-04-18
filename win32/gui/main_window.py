"""
Main Window Module
Main application window for Windows desktop GUI.
"""

import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from loguru import logger

# Установка офлайн-режима
os.environ['HF_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

from processor import MedicalAudioProcessor
from styles import apply_app_theme, COLORS, STYLES

logger.info("Main Window initialized")


class MainWindow(ctk.CTk):
    """Главное окно приложения."""

    def __init__(self):
        """Инициализация главного окна."""
        super().__init__()

        self.title("🏥 Qwen Medical Transcriber")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Инициализация процессора
        self.processor = None
        self.file_list: List[str] = []
        self.progress_dialog = None

        # Настройка темы
        apply_app_theme(self)

        # Создание интерфейса
        self._create_layout()
        self._create_menu()
        self._create_header()
        self._create_file_list()
        self._create_controls()
        self._create_status_bar()

        # Загрузка настроек
        self._load_settings()

        logger.info("Main Window created successfully")

    def _create_layout(self):
        """Создать основную структуру макета."""
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_menu(self):
        """Создать меню."""
        menubar = ctk.CTkMenu(self)
        self.configure(menu=menubar)

        # Файл
        file_menu = ctk.CTkMenu(menubar)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Добавить файл", command=self._add_files)
        file_menu.add_command(label="Очистить список", command=self._clear_files)
        file_menu.add_separator()
        file_menu.add_command(label="Настройки", command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)

        # Обработка
        process_menu = ctk.CTkMenu(menubar)
        menubar.add_cascade(label="Обработка", menu=process_menu)
        process_menu.add_command(label="Обработать все", command=self._process_all)
        process_menu.add_command(label="Отмена", command=self._cancel_processing)

        # Справка
        help_menu = ctk.CTkMenu(menubar)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
        help_menu.add_command(label="Инструкция", command=self._show_help)

    def _create_header(self):
        """Создать заголовок."""
        header_frame = ctk.CTkFrame(self, **STYLES['frame'])
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Заголовок
        title_label = ctk.CTkLabel(
            header_frame,
            text="🏥 Qwen Medical Transcriber",
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=10)

        # Описание
        desc_label = ctk.CTkLabel(
            header_frame,
            text="Профессиональная система транскрибации медицинских консультаций",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        desc_label.pack()

    def _create_file_list(self):
        """Создать список файлов."""
        file_list_frame = ctk.CTkFrame(self, **STYLES['frame'])
        file_list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        file_list_frame.grid_rowconfigure(0, weight=1)
        file_list_frame.grid_columnconfigure(0, weight=1)

        # Заголовок списка
        list_header = ctk.CTkLabel(
            file_list_frame,
            text="Файлы для обработки",
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary']
        )
        list_header.pack(pady=10, padx=10, anchor="w")

        # Treeview для списка файлов
        self.file_tree = ttk.Treeview(
            file_list_frame,
            columns=("file", "status", "size"),
            show="tree headings",
            height=8
        )

        # Колонки
        self.file_tree.heading("#0", text="Файл", anchor="w")
        self.file_tree.heading("file", text="Файл", anchor="w")
        self.file_tree.heading("status", text="Статус", anchor="w")
        self.file_tree.heading("size", text="Размер", anchor="e")

        # Ширина колонок
        self.file_tree.column("#0", width=200, minwidth=150)
        self.file_tree.column("file", width=200, minwidth=150)
        self.file_tree.column("status", width=100, minwidth=80)
        self.file_tree.column("size", width=80, minwidth=60, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.file_tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления списком
        list_btn_frame = ctk.CTkFrame(file_list_frame, fg_color="transparent")
        list_btn_frame.pack(pady=10)

        add_btn = ctk.CTkButton(
            list_btn_frame,
            text="+ Добавить",
            command=self._add_files,
            **STYLES['button_primary']
        )
        add_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            list_btn_frame,
            text="Очистить",
            command=self._clear_files,
            **STYLES['button_secondary']
        )
        clear_btn.pack(side="left", padx=5)

    def _create_controls(self):
        """Создать панель управления."""
        controls_frame = ctk.CTkFrame(self, **STYLES['frame'])
        controls_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        # Настройки
        settings_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Язык
        lang_label = ctk.CTkLabel(settings_frame, text="Язык:", width=80)
        lang_label.pack(side="left", padx=(0, 5))
        self.lang_combo = ctk.CTkComboBox(
            settings_frame,
            values=["Русский", "Английский", "Автоматическое"],
            width=120,
            **STYLES['combobox']
        )
        self.lang_combo.pack(side="left", padx=5)
        self.lang_combo.set("Русский")

        # Спикеры
        speakers_label = ctk.CTkLabel(settings_frame, text="Спикеры:", width=80)
        speakers_label.pack(side="left", padx=(20, 5))
        self.speakers_var = ctk.StringVar(value="2")
        speakers_spin = ctk.CTkSpinBox(
            settings_frame,
            from_=1,
            to=10,
            variable=self.speakers_var,
            width=60
        )
        speakers_spin.pack(side="left", padx=5)

        # Галочки
        self.alignment_var = ctk.BooleanVar(value=True)
        alignment_check = ctk.CTkCheckBox(
            settings_frame,
            text="Forced Alignment",
            variable=self.alignment_var
        )
        alignment_check.pack(side="left", padx=20)

        self.timestamps_var = ctk.BooleanVar(value=True)
        timestamps_check = ctk.CTkCheckBox(
            settings_frame,
            text="Таймкоды",
            variable=self.timestamps_var
        )
        timestamps_check.pack(side="left", padx=5)

        # Кнопка запуска
        process_btn = ctk.CTkButton(
            controls_frame,
            text="🚀 Обработать",
            command=self._process_all,
            **STYLES['button_primary']
        )
        process_btn.pack(pady=10, padx=10, side="right")

    def _create_status_bar(self):
        """Создать строку статуса."""
        self.status_bar = ctk.CTkFrame(self, height=30, fg_color="#f1f5f9")
        self.status_bar.grid(row=3, column=0, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Готов к работе",
            text_color=COLORS['text_secondary'],
            font=('Segoe UI', 10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(
            self.status_bar,
            mode="determinate",
            maximum=100
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.progress_bar.pack_forget()  # Скрыть по умолчанию

    def _add_files(self):
        """Добавить файлы в список."""
        filetypes = (
            ("Аудио файлы", "*.wav *.mp3 *.flac *.m4a *.ogg"),
            ("WAV файлы", "*.wav"),
            ("MP3 файлы", "*.mp3"),
            ("FLAC файлы", "*.flac"),
            ("M4A файлы", "*.m4a"),
            ("OGG файлы", "*.ogg"),
            ("Все файлы", "*.*")
        )

        files = filedialog.askopenfilenames(
            title="Выберите аудио файлы",
            filetypes=filetypes
        )

        for file in files:
            if file not in self.file_list:
                self.file_list.append(file)
                self._add_to_tree(file)

    def _add_to_tree(self, file_path: str):
        """Добавить файл в treeview."""
        try:
            size = os.path.getsize(file_path)
            size_str = self._format_size(size)
            filename = os.path.basename(file_path)

            item = self.file_tree.insert(
                "",
                "end",
                text=filename,
                values=(filename, "Ожидание", size_str)
            )
            self.file_tree.item(item, tags=file_path)
        except Exception as e:
            logger.error(f"Ошибка добавления файла {file_path}: {e}")

    def _clear_files(self):
        """Очистить список файлов."""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.file_list.clear()

    def _process_all(self):
        """Обработать все файлы."""
        if not self.file_list:
            messagebox.showwarning("Предупреждение", "Список файлов пуст")
            return

        # Получить настройки
        language = self._get_language()
        num_speakers = int(self.speakers_var.get())
        use_alignment = self.alignment_var.get()
        include_timestamps = self.timestamps_var.get()

        # Запуск обработки
        self._show_progress_dialog()

        # Инициализация процессора
        if self.processor is None:
            self._init_processor()

        try:
            success_count = 0
            error_count = 0

            for file_path in self.file_list:
                filename = os.path.basename(file_path)
                self._update_status(f"Обработка: {filename}")

                # Обновить статус в tree
                for item in self.file_tree.get_children():
                    if self.file_tree.item(item, "values")[0] == filename:
                        self.file_tree.item(item, values=(filename, "Обработка...", ""))

                try:
                    result = self.processor.process_file(
                        file_path,
                        language=language,
                        num_speakers=num_speakers,
                        use_alignment=use_alignment
                    )

                    if result['success']:
                        success_count += 1
                        for item in self.file_tree.get_children():
                            if self.file_tree.item(item, "values")[0] == filename:
                                self.file_tree.item(item, values=(filename, "Готово", ""))

                    else:
                        error_count += 1
                        for item in self.file_tree.get_children():
                            if self.file_tree.item(item, "values")[0] == filename:
                                self.file_tree.item(item, values=(filename, f"Ошибка: {result.get('error', 'Unknown')}", ""))

                except Exception as e:
                    error_count += 1
                    logger.error(f"Ошибка обработки {file_path}: {e}")
                    for item in self.file_tree.get_children():
                        if self.file_tree.item(item, "values")[0] == filename:
                            self.file_tree.item(item, values=(filename, f"Ошибка: {str(e)}", ""))

            # Показать результат
            self._hide_progress_dialog()
            self._update_status(f"Обработка завершена: {success_count} успешно, {error_count} ошибок")

            if success_count > 0:
                messagebox.showinfo(
                    "Готово",
                    f"Успешно обработано: {success_count}\nОшибок: {error_count}"
                )

        except Exception as e:
            self._hide_progress_dialog()
            messagebox.showerror("Ошибка", f"Критическая ошибка: {str(e)}")
            logger.error(f"Критическая ошибка: {e}")

    def _init_processor(self):
        """Инициализировать процессор."""
        try:
            from processor import MedicalAudioProcessor
            self.processor = MedicalAudioProcessor()
            logger.info("MedicalAudioProcessor initialized")
        except Exception as e:
            logger.error(f"Ошибка инициализации процессора: {e}")
            raise

    def _get_language(self) -> str:
        """Получить код языка из combo."""
        lang_map = {
            "Русский": "ru",
            "Английский": "en",
            "Автоматическое": "auto"
        }
        return lang_map.get(self.lang_combo.get(), "ru")

    def _format_size(self, size_bytes: int) -> str:
        """Форматировать размер файла."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _update_status(self, message: str):
        """Обновить статус в строке статуса."""
        self.status_label.configure(text=message)

    def _show_progress_dialog(self):
        """Показать диалог прогресса."""
        if self.progress_dialog is None:
            self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()

    def _hide_progress_dialog(self):
        """Скрыть диалог прогресса."""
        if self.progress_dialog:
            self.progress_dialog.hide()

    def _show_log_window(self):
        """Показать окно логов."""
        log_window = ctk.CTkToplevel(self)
        log_window.title("Логи")
        log_window.geometry("600x400")

        # Text widget для логов
        log_text = ctk.CTkTextbox(log_window, font=('Consolas', 10))
        log_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Загрузка логов
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
            log_file = os.path.join(log_dir, 'log_*.log')

            # Простой вывод последнего лога
            log_text.insert("1.0", "Логи будут доступны после обработки файлов")

        except Exception as e:
            log_text.insert("1.0", f"Ошибка загрузки логов: {e}")

        log_text.configure(state="disabled")

    def _open_settings(self):
        """Открыть окно настроек."""
        from settings_window import SettingsWindow
        settings = SettingsWindow(self)
        self.wait_window(settings)

    def _show_about(self):
        """Показать окно 'О программе'."""
        about = ctk.CTkToplevel(self)
        about.title("О программе")
        about.geometry("400x300")

        # Центрирование
        about.update_idletasks()
        x = (about.winfo_screenwidth() // 2) - (400 // 2)
        y = (about.winfo_screenheight() // 2) - (300 // 2)
        about.geometry(f'400x300+{x}+{y}')

        # Содержимое
        frame = ctk.CTkFrame(about, **STYLES['frame'])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_label = ctk.CTkLabel(frame, text="🏥", font=('Segoe UI', 60))
        icon_label.pack(pady=10)

        title_label = ctk.CTkLabel(
            frame,
            text="Qwen Medical Transcriber",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack()

        version_label = ctk.CTkLabel(
            frame,
            text="Версия 2.0.0",
            text_color=COLORS['text_secondary']
        )
        version_label.pack(pady=5)

        desc_label = ctk.CTkLabel(
            frame,
            text="Профессиональная система транскрибации медицинских консультаций\n"
                 "с разделением диалога по ролям Врач/Пациент.\n\n"
                 "Полностью офлайн-работа. Модели загружаются локально.",
            text_color=COLORS['text_secondary'],
            wraplength=300,
            justify="center"
        )
        desc_label.pack(pady=10)

        close_btn = ctk.CTkButton(
            frame,
            text="Закрыть",
            command=about.destroy,
            **STYLES['button_secondary']
        )
        close_btn.pack(pady=10)

    def _show_help(self):
        """Показать справку."""
        help_text = """
        Инструкция по использованию:

        1. Добавьте аудио файлы (WAV, MP3, FLAC, M4A, OGG)
        2. Выберите язык (Русский/Английский/Авто)
        3. Укажите количество спикеров
        4. Нажмите "Обработать"

        Результаты:
        - DOCX файл с диалогом
        - Данные в строке статуса

        Требования:
        - Аудио должно быть на русском или английском языке
        - Минимальная длительность: 1 секунда
        - Максимальный размер: 500 MB
        """
        messagebox.showinfo("Инструкция", help_text)

    def _load_settings(self):
        """Загрузить настройки из файла."""
        settings_file = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Применить настройки
            except Exception as e:
                logger.error(f"Ошибка загрузки настроек: {e}")

    def _save_settings(self):
        """Сохранить настройки в файл."""
        settings = {
            'language': self.lang_combo.get(),
            'num_speakers': int(self.speakers_var.get()),
            'use_alignment': self.alignment_var.get(),
            'include_timestamps': self.timestamps_var.get(),
        }

        settings_file = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")

    def quit(self):
        """Выход из приложения."""
        self._save_settings()
        super().quit()


class ProgressDialog:
    """Диалоговое окно прогресса."""

    def __init__(self, parent: ctk.CTk):
        """Инициализация диалога."""
        self.parent = parent
        self.window = None
        self.progress_bar = None
        self.status_label = None

    def show(self):
        """Показать диалог."""
        if self.window is None:
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Обработка")
            self.window.geometry("400x150")
            self.window.transient(self.parent)
            self.window.grab_set()

            # Прогресс бар
            self.progress_bar = ttk.Progressbar(
                self.window,
                mode="indeterminate",
                maximum=100
            )
            self.progress_bar.pack(fill="x", padx=20, pady=20)
            self.progress_bar.start()

            # Статус
            self.status_label = ctk.CTkLabel(
                self.window,
                text="Обработка файлов...",
                text_color=COLORS['text_secondary']
            )
            self.status_label.pack(pady=10)

        self.window.deiconify()

    def hide(self):
        """Скрыть диалог."""
        if self.window:
            self.window.withdraw()

    def set_status(self, message: str):
        """Обновить статус."""
        if self.status_label:
            self.status_label.configure(text=message)


if __name__ == "__main__":
    # Запуск приложения
    app = MainWindow()
    app.mainloop()
