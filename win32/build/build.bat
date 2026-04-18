@echo off
REM Build script for Windows installer
REM Compiles Python code and creates executable

setlocal enabledelayedexpansion

echo ========================================
echo Qwen Medical Transcriber - Build Script
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

echo [1/4] Checking dependencies...
python -c "import customtkinter; import gradio; import docx" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r ..\requirements-win32.txt
    if %errorlevel% neq 0 (
        echo WARNING: Some dependencies may be missing
    )
)

echo [2/4] Cleaning old build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Create build directory
if not exist build mkdir build
if not exist dist mkdir dist

echo [3/4] Building executable with PyInstaller...
python -m PyInstaller ^
    --name="QwenTranscriber" ^
    --windowed ^
    --noconsole ^
    --onefile ^
    --add-data="../win32/gui;win32/gui" ^
    --add-data="../app;app" ^
    --hidden-import=qwen_asr ^
    --hidden-import=transformers ^
    --hidden-import=torch ^
    --hidden-import=torchaudio ^
    --hidden-import=customtkinter ^
    --hidden-import=gradio ^
    --hidden-import=docx ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=pyannote.audio ^
    --hidden-import=soundfile ^
    --hidden-import=librosa ^
    --hidden-import=loguru ^
    --icon=../win32/resources/icon.ico ^
    --distpath=dist ^
    --workpath=build ^
    --specpath=. ^
    ../win32/gui/main_window.py

if %errorlevel% neq 0 (
    echo ERROR: PyInstaller failed
    exit /b 1
)

echo [4/4] Copying models directory (optional)...
if exist ..\models (
    if exist dist\models (
        rmdir /s /q dist\models
    )
    xcopy /E /I /Y ..\models dist\models
)

echo ========================================
echo Build completed!
echo Executable: dist\QwenTranscriber.exe
echo ========================================

REM Clean up temporary files
if exist build rmdir /s /q build

echo Done.
