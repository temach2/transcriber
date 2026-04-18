"""
Progress Dialog Module
Progress dialog for displaying processing status.
"""

import customtkinter as ctk
from typing import Optional, Callable
from loguru import logger


class ProgressDialog:
    """Диалоговое окно для отображения прогресса обработки."""

    def __init__(
        self,
        parent: ctk.CTk,
        title: str = "Обработка",
        max_value: int = 100
    ):
        """
        Инициализация диалога прогресса.

        Args:
            parent: Родительское окно
            title: Заголовок окна
            max_value: Максимальное значение прогресса
        """
        self.parent = parent
        self.title = title
        self.max_value = max_value

        self.window: Optional[ctk.CTkToplevel] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.log_text: Optional[ctk.CTkTextbox] = None

        self._is_running = False
        self._log_messages = []

    def show(self):
        """Показать диалог."""
        if self.window is not None:
            self.window.deiconify()
            return

        # Создание окна
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(self.title)
        self.window.geometry("500x350")
        self.window.resizable(False, False)

        # Центрирование
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 250
        y = (self.window.winfo_screenheight() // 2) - 175
        self.window.geometry(f'500x350+{x}+{y}')

        # Принудительный фокус
        self.window.transient(self.parent)
        self.window.grab_set()

        # Создание интерфейса
        self._create_layout()

        self._is_running = True
        logger.info("ProgressDialog shown")

    def hide(self):
        """Скрыть диалог."""
        if self.window:
            self.window.withdraw()
        self._is_running = False
        logger.info("ProgressDialog hidden")

    def close(self):
        """Закрыть диалог."""
        if self.window:
            self.window.destroy()
            self.window = None
        self._is_running = False
        logger.info("ProgressDialog closed")

    def update_progress(self, value: float, message: str = None):
        """
        Обновить прогресс и статус.

        Args:
            value: Текущее значение прогресса (0-100)
            message: Сообщение статуса
        """
        if not self._is_running or self.window is None:
            return

        if self.progress_bar:
            self.progress_bar.set(value / self.max_value)

        if message and self.status_label:
            self.status_label.configure(text=message)
            self._add_log(message)

    def set_status(self, message: str):
        """Установить сообщение статуса."""
        if self.status_label:
            self.status_label.configure(text=message)
            self._add_log(message)

    def _create_layout(self):
        """Создать макет диалога."""
        # Прогресс бар
        progress_frame = ctk.CTkFrame(self.window, corner_radius=0)
        progress_frame.pack(fill="x", padx=20, pady=20)

        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=10,
            corner_radius=5
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        # Статус
        status_frame = ctk.CTkFrame(self.window, corner_radius=0, fg_color="transparent")
        status_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Инициализация...",
            text_color="#64748b"
        )
        self.status_label.pack()

        # Логи
        log_frame = ctk.CTkFrame(self.window, corner_radius=8, border_width=1, border_color="#e2e8f0")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            log_frame,
            text="Логи обработки:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=10, pady=10)

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=("Consolas", 9),
            height=150,
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Кнопка закрытия (скрыта, пока не завершено)
        self.close_btn = ctk.CTkButton(
            self.window,
            text="Закрыть",
            command=self.close,
            width=100,
            state="disabled"
        )
        self.close_btn.pack(pady=10)

    def _add_log(self, message: str):
        """Добавить сообщение в лог."""
        self._log_messages.append(message)

        # Ограничить количество сообщений
        if len(self._log_messages) > 100:
            self._log_messages = self._log_messages[-100:]

        # Обновить текст
        if self.log_text:
            self.log_text.configure(state="normal")
            self.log_text.insert("end", f"[{self._get_time()}] {message}\n")
            self.log_text.configure(state="disabled")
            self.log_text.see("end")

    def _get_time(self) -> str:
        """Получить текущее время в формате HH:MM:SS."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def is_running(self) -> bool:
        """Проверить, запущен ли диалог."""
        return self._is_running

    def reset(self):
        """Сбросить диалог."""
        if self.progress_bar:
            self.progress_bar.set(0)
        if self.status_label:
            self.status_label.configure(text="Инициализация...")
        if self.log_text:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.configure(state="disabled")
        self._log_messages = []


def show_processing_progress(
    parent: ctk.CTk,
    callback: Callable[[ProgressDialog], None]
):
    """
    Показать диалог прогресса и выполнить callback.

    Args:
        parent: Родительское окно
        callback: Функция обработки, принимающая ProgressDialog
    """
    progress = ProgressDialog(parent)

    def on_start():
        progress.show()
        try:
            callback(progress)
        finally:
            progress.close_btn.configure(state="normal")

    parent.after(100, on_start)


if __name__ == "__main__":
    # Тест
    import time

    def test_callback(progress: ProgressDialog):
        for i in range(101):
            progress.update_progress(i, f"Обработка {i}%...")
            time.sleep(0.05)

    app = ctk.CTk()
    app.withdraw()
    show_processing_progress(app, test_callback)
    app.mainloop()
