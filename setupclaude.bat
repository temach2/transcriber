@echo off
rem -------------------------------------------------
rem  run_claude.bat – выбор сервера и запуск Claude
rem  Работает в директории, где находится файл.
rem  Сохраняйте как UTF‑8 без BOM.
rem -------------------------------------------------

rem ------------------------------------------------------------------
rem 1. Переходим в директорию скрипта (чтобы относительные пути работали)
pushd "%~dp0"

rem ------------------------------------------------------------------
rem 2. Устанавливаем кодовую страницу UTF‑8 (нужна для корректного вывода кириллицы)
chcp 65001 >nul

rem ------------------------------------------------------------------
rem 3. Обрабатываем "быстрый" запуск (опционально)
if "%~1"=="-f" goto fast_launch
if "%~1"=="--fast" goto fast_launch

@echo off
:menu
cls
echo =========================================
echo     Меню запуска Claude Code
echo =========================================
echo Выберите провайдера:
echo.
echo [1] OpenRouter (nemotron-3-super-120b)
echo [2] Ollama (qwen3-coder-next:cloud)
echo [3] Ollama (llama3.1:8b)
echo [4] Ollama (llama3.2:3b)
echo.
set /p choice="Ваш выбор: "

if "%choice%"=="1" goto openrouter1
if "%choice%"=="2" goto ollama1
if "%choice%"=="3" goto ollama2
if "%choice%"=="4" goto ollama3
echo Неверный выбор. Попробуйте снова.
pause
goto menu

:openrouter1
cls
echo =========================================
echo  Настройка для OpenRouter
echo =========================================
echo.

:: 1. Установка переменных окружения для OpenRouter
set "ANTHROPIC_BASE_URL=http://localhost:8787"
set "ANTHROPIC_API_KEY=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"
set "ANTHROPIC_CUSTOM_HEADERS=x-api-key: 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"
set "ANTHROPIC_MODEL=nvidia/nemotron-3-super-120b-a12b:free"
goto check_and_launch


:ollama1
cls
echo =========================================
echo  Настройка для Ollama
echo =========================================
echo.
:: 1. Установка переменных окружения для Ollama
set "ANTHROPIC_BASE_URL=http://localhost:11434"
set "ANTHROPIC_AUTH_TOKEN=f105c328e888448b926d4121dd7f6ff6.LZgQIzMePfH0IJ43qIyGDc5n"
set "ANTHROPIC_MODEL=qwen3-coder-next:cloud"
goto check_and_launch

:ollama2
cls
echo =========================================
echo  Настройка для Ollama
echo =========================================
echo.
:: 1. Установка переменных окружения для Ollama
set "ANTHROPIC_BASE_URL=http://localhost:11434"
set "ANTHROPIC_AUTH_TOKEN=f105c328e888448b926d4121dd7f6ff6.LZgQIzMePfH0IJ43qIyGDc5n"
set "ANTHROPIC_MODEL=llama3.1:8b"
goto check_and_launch

:ollama3
cls
echo =========================================
echo  Настройка для Ollama
echo =========================================
echo.
:: 1. Установка переменных окружения для Ollama
set "ANTHROPIC_BASE_URL=http://localhost:11434"
set "ANTHROPIC_AUTH_TOKEN=f105c328e888448b926d4121dd7f6ff6.LZgQIzMePfH0IJ43qIyGDc5n"
set "ANTHROPIC_MODEL=llama3.2:3b"
goto check_and_launch

rem ------------------------------------------------------------------
rem 6. Быстрый запуск (если передан -f/--fast)
:fast_launch
rem Здесь задаём «по‑умолчанию» – можно менять под свои нужды
set "ANTHROPIC_BASE_URL=http://localhost:11434"
set "ANTHROPIC_API_KEY=f105c328e888448b926d4121dd7f6ff6.LZgQIzMePfH0IJ43qIyGDc5n"
set "ANTHROPIC_MODEL=qwen3-coder-next:cloud"
echo [Быстрый запуск] Выбран сервер %ANTHROPIC_BASE_URL%
goto check_and_launch

rem ------------------------------------------------------------------
rem 7. Проверяем, что утилита `claude` доступна в PATH
:check_and_launch
where claude >nul 2>&1
if errorlevel 1 (
    echo Ошибка: исполняемый файл ^"claude^" не найден в PATH.
    popd
    exit /b 1
)

rem ------------------------------------------------------------------
rem 8. Запускаем Claude с выбранной моделью
:launch
echo.
echo --------------------------------------------------
echo Запуск Claude с параметрами:
echo   SERVER      = %ANTHROPIC_BASE_URL%
echo   API‑KEY     = %ANTHROPIC_API_KEY%
echo   HEADERS     = %ANTHROPIC_CUSTOM_HEADERS%
echo   MODEL       = %ANTHROPIC_MODEL%
echo --------------------------------------------------
claude 
if errorlevel 1 (
    echo Ошибка: команда ^"claude^" завершилась с ошибкой.
    popd
    exit /b 1
)

rem ------------------------------------------------------------------
rem 9. Возвращаемся в исходную директорию и завершаемся
popd
exit /b