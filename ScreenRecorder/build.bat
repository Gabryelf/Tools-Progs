@echo off
echo Сборка Screen Recorder...

REM Очистка старых сборок
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Сборка с явным указанием всех путей
pyinstaller --onefile --windowed --name ScreenRecorder ^
    --add-data "assets;assets" ^
    --add-data "config;config" ^
    --icon assets/icon.ico ^
    --hidden-import=gui ^
    --hidden-import=gui.main_window ^
    --hidden-import=gui.drawing_toolbar ^
    --hidden-import=gui.modern_styles ^
    --hidden-import=gui.styles ^
    --hidden-import=core ^
    --hidden-import=core.settings ^
    --hidden-import=core.recorder ^
    --hidden-import=core.audio_processor ^
    --hidden-import=utils ^
    --hidden-import=utils.helpers ^
    --hidden-import=sounddevice ^
    --hidden-import=soundfile ^
    --hidden-import=pyautogui ^
    --hidden-import=moviepy ^
    --hidden-import=moviepy.editor ^
    --hidden-import=scipy ^
    --hidden-import=scipy.signal ^
    --hidden-import=numpy ^
    --hidden-import=cv2 ^
    --hidden-import=PIL ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    main.py

echo Готово! EXE файл в папке dist\
pause
