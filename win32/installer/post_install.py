"""
Post-Install Script
Executes after the Windows installer completes.
"""

import os
import sys
import subprocess
import winreg
from pathlib import Path
from loguru import logger


def get_install_dir() -> str:
    """Получить директорию установки из реестра."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Qwen Medical Transcriber",
            0,
            winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, "InstallDir")
            return value
    except Exception as e:
        logger.error(f"Ошибка чтения реестра: {e}")
        return None


def create_shortcuts(install_dir: str):
    """Создать ярлыки на рабочем столе и в меню Пуск."""
    import win32com.client

    shell = win32com.client.Dispatch("WScript.Shell")

    # Путь к исполняемому файлу
    exe_path = os.path.join(install_dir, "QwenTranscriber.exe")

    # Ярлык на рабочем столе
    desktop = Path.home() / "Desktop"
    desktop_shortcut = str(desktop / "Qwen Medical Transcriber.lnk")

    shortcut = shell.CreateShortCut(desktop_shortcut)
    shortcut.Targetpath = exe_path
    shortcut.WorkingDirectory = install_dir
    shortcut.Description = "Qwen Medical Transcriber - Система транскрибации медицинских консультаций"
    shortcut.Save()

    logger.info(f"Ярлык на рабочем столе создан: {desktop_shortcut}")

    # Ярлык в меню Пуск
    start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    start_menu.mkdir(parents=True, exist_ok=True)
    start_menu_shortcut = str(start_menu / "Qwen Medical Transcriber.lnk")

    shortcut = shell.CreateShortCut(start_menu_shortcut)
    shortcut.Targetpath = exe_path
    shortcut.WorkingDirectory = install_dir
    shortcut.Save()

    logger.info(f"Ярлык в меню Пуск создан: {start_menu_shortcut}")


def setup_models_dir(install_dir: str) -> bool:
    """Настроить директорию для моделей."""
    models_dir = os.path.join(install_dir, "models")

    try:
        os.makedirs(models_dir, exist_ok=True)

        # Создать файл инструкции
        readme_path = os.path.join(models_dir, "README.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("""Директория моделей

Для работы приложения требуется разместить следующие модели:
- Qwen3-ASR-1.7B
- Qwen3-ForcedAligner-0.6B
- pyannote-speaker-diarization-3.1

Модели можно загрузить с Hugging Face и разместить в этой директории.
""")

        logger.info(f"Директория моделей настроена: {models_dir}")
        return True

    except Exception as e:
        logger.error(f"Ошибка настройки директории моделей: {e}")
        return False


def register_uninstall(install_dir: str):
    """Регистрация удаления в системе."""
    try:
        with winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\QwenMedicalTranscriber"
        ) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Qwen Medical Transcriber")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,
                            f"msiexec /x {{GUID}}")  # Уникальный GUID
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ,
                            os.path.join(install_dir, "QwenTranscriber.exe"))
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Qwen Medical Team")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "2.0.0")

        logger.info("Установка зарегистрирована в системе")
    except Exception as e:
        logger.error(f"Ошибка регистрации uninstall: {e}")


def main():
    """Основная функция пост-установки."""
    logger.info("Запуск post-install скрипта")

    # Получить директорию установки
    install_dir = get_install_dir()
    if not install_dir:
        # Если не удалось получить из реестра, использовать текущую директорию
        install_dir = os.path.dirname(sys.executable)

    logger.info(f"Директория установки: {install_dir}")

    # Настроить директорию моделей
    setup_models_dir(install_dir)

    # Создать ярлыки
    try:
        create_shortcuts(install_dir)
    except Exception as e:
        logger.warning(f"Не удалось создать ярлыки: {e}")

    # Зарегистрировать удаление
    register_uninstall(install_dir)

    logger.info("Post-install скрипт завершен")

    # Показать сообщение пользователю (если запущен из installer)
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            "Установка завершена!\n\n"
            "Модели должны быть размещены в папке models/ вручную или загружены через приложение.",
            "Qwen Medical Transcriber",
            0x40
        )
    except Exception as e:
        logger.warning(f"Не удалось показать сообщение: {e}")


if __name__ == "__main__":
    main()
