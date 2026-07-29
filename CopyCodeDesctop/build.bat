@echo off
title Copy Code Pro Builder

echo ========================================
echo   Сборка Copy Code Pro
echo ========================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    pause
    exit /b 1
)

:: Установка зависимостей
echo 1. Установка зависимостей...
pip install -r requirements.txt

:: Сборка с использованием spec файла
echo 2. Сборка EXE с ресурсами...
pyinstaller copy_code_pro.spec

:: Проверка результата
if exist dist\CopyCodePro.exe (
    echo.
    echo ========================================
    echo   ✅ Сборка успешно завершена!
    echo   📁 Файл: dist\CopyCodePro.exe
    echo   📁 Размер:
    for %%A in ("dist\CopyCode-v004.exe") do echo   %%A
    echo ========================================

    :: Создание ZIP с ресурсами
    echo.
    echo 3. Создание ZIP архива для распространения...
    cd dist
    mkdir CopyCodePro_Files
    copy CopyCodePro.exe CopyCodePro_Files\
    cd ..
    echo.
    echo ========================================
    echo   Готово!
    echo   EXE файл: dist\CopyCodePro-v004.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   ❌ Ошибка сборки!
    echo ========================================
)

pause