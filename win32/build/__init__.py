# Qwen Medical Transcriber - Build Module
"""
Build configuration for PyInstaller.
"""

import os
import sys
from pathlib import Path

# Основные настройки
APP_NAME = "QwenTranscriber"
APP_VERSION = "2.0.0"

# Пути
BASE_DIR = Path(__file__).parent.parent
APP_DIR = BASE_DIR / "app"
WIN32_DIR = BASE_DIR / "win32"
RESOURCES_DIR = WIN32_DIR / "resources"

# Скрытые импорты (для PyInstaller)
HIDDEN_IMPORTS = [
    # ASR
    "qwen_asr",
    "transformers",
    "torch",
    "torchaudio",
    "accelerate",
    "huggingface_hub",
    "tokenizers",

    # Diarization
    "pyannote.audio",
    "pyannote.core",
    "pyannote.metrics",
    "diart",

    # GUI
    "customtkinter",
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "PIL",
    "PIL._imaging",
    "PIL._tkinter_finder",

    # Audio
    "soundfile",
    "librosa",
    "audioread",
    "ffmpeg",
    "av",

    # Document
    "docx",
    "docx.oxml",
    "docx.shared",

    # Web
    "gradio",
    "gradio.routes",
    "gradio.helpers",
    "uvicorn",
    "websockets",

    # Utilities
    "loguru",
    "tqdm",
    "yaml",
    "numpy",
    "scipy",
    "sounddevice",
]

# Исключения
EXCLUDES = [
    "tkinter.test",
    "tkinter.tix",
    "distutils",
    "unittest",
    "pydoc",
    "bdb",
    "pdb",
    "cProfile",
    "profile",
    "test",
    "tests",
]

# Данные (файлы, не являющиеся кодом)
DATA_FILES = [
    # Resources
    (str(RESOURCES_DIR / "*.ico"), "resources"),
    (str(RESOURCES_DIR / "*.png"), "resources"),
    (str(RESOURCES_DIR / "*.jpg"), "resources"),
]


def get_spec_file_path():
    """Получить путь к .spec файлу."""
    return BASE_DIR / "win32" / "build" / f"{APP_NAME}.spec"


def create_spec_file():
    """Создать .spec файл для PyInstaller."""
    spec_content = f'''# -*- coding: utf-8 -*-
"""
PyInstaller Specification for {APP_NAME}
Auto-generated specification file.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Пути
block_cipher = None
app_name = "{APP_NAME}"
app_version = "{APP_VERSION}"

# Получить пути к данным
datas = []
binaries = []
hiddenimports = {HIDDEN_IMPORTS!r}

# Сбор данных из модулей
try:
    datas += collect_data_files('customtkinter')
    datas += collect_data_files('tkinter')
    datas += collect_data_files('PIL')
    datas += collect_data_files('soundfile')
    datas += collect_data_files('docx')
except Exception as e:
    print(f"Warning collecting data: {{e}}")

# Основной скрипт
a = Analysis(
    ['main_window.py'],
    pathex=[os.path.dirname(os.path.abspath(__file__)), os.path.abspath('..')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter.test', 'tkinter.tix', 'distutils', 'unittest', 'pydoc', 'test', 'tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    run_viewer=False,
    console=False,  # Без консольного окна
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    spec_path = get_spec_file_path()
    os.makedirs(spec_path.parent, exist_ok=True)

    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print(f"Spec файл создан: {spec_path}")
    return str(spec_path)


def build_exe():
    """Собрать .exe файл."""
    import subprocess
    import shutil

    spec_path = get_spec_file_path()

    if not spec_path.exists():
        print(f"Spec файл не найден: {spec_path}")
        print("Создание spec файла...")
        create_spec_file()

    # Команда PyInstaller
    cmd = [
        "pyinstaller",
        str(spec_path),
        "--clean",
    ]

    print(f"Запуск PyInstaller: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"Сборка завершена. Файл в dist/{APP_NAME}.exe")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка сборки: {e}")
        print(e.stderr)
        raise


def clean_build():
    """Очистить старые артефакты сборки."""
    dirs_to_clean = [
        BASE_DIR / "build",
        BASE_DIR / "dist",
        BASE_DIR / "__pycache__",
    ]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"Удаление: {dir_path}")
            shutil.rmtree(dir_path)

    # Удалить .spec файлы
    for spec_file in BASE_DIR.glob("*.spec"):
        print(f"Удаление: {spec_file}")
        spec_file.unlink()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build configuration for PyInstaller")
    parser.add_argument("command", choices=["build", "clean", "create-spec"], help="Команда")
    args = parser.parse_args()

    if args.command == "build":
        build_exe()
    elif args.command == "clean":
        clean_build()
    elif args.command == "create-spec":
        create_spec_file()
