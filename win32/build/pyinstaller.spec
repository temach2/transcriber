# -*- coding: utf-8 -*-
"""
PyInstaller Specification for QwenTranscriber
Windows desktop application for medical transcription.
"""

import os
import sys

# Путь к базовой директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Скрытые импорты для PyInstaller
hiddenimports = [
    # Core dependencies
    'qwen_asr',
    'transformers',
    'torch',
    'torchaudio',
    'accelerate',
    'huggingface_hub',
    'tokenizers',

    # Diarization
    'pyannote.audio',
    'pyannote.core',
    'pyannote.metrics',
    'diart',

    # GUI
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'PIL',
    'PIL._imaging',
    'PIL._tkinter_finder',

    # Audio processing
    'soundfile',
    'librosa',
    'audioread',
    'ffmpeg',
    'av',
    'numpy',
    'scipy',

    # Document generation
    'docx',
    'docx.oxml',
    'docx.shared',
    'docx.table',
    'docx.text',

    # Web interface
    'gradio',
    'gradio.routes',
    'gradio.helpers',
    'gradio.exceptions',
    'gradio.components',
    'gradio.blocks',
    'gradio.events',
    'uvicorn',
    'uvicorn.lifespan.on',
    'websockets',
    'websockets.server',
    'websockets.protocol',

    # Utilities
    'loguru',
    'tqdm',
    'yaml',
    'ctypes',
]

# Данные (non-code files)
datas = [
    # CustomTKinter themes and assets
    ('venv/Lib/site-packages/customtkinter', 'customtkinter'),
    # Tkinter assets (if needed)
]

# Исключения (не включать в .exe)
excludes = [
    'tkinter.test',
    'tkinter.tix',
    'distutils',
    'unittest',
    'pydoc',
    'bdb',
    'pdb',
    'cProfile',
    'profile',
    'test',
    'tests',
]

# Сборка
block_cipher = None

a = Analysis(
    ['../win32/gui/main_window.py'],
    pathex=[BASE_DIR, os.path.abspath('..')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
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
    name='QwenTranscriber',
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
