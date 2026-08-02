"""
Setup файл для установки
"""
from setuptools import setup, find_packages
import os

# Чтение README
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_path, 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="screen-recorder",
    version="0.0.4",
    author="Gabryelf",
    description="Запись экрана с системным звуком",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gabryelf/Tools-Progs",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "sounddevice>=0.4.0",
        "soundfile>=0.10.0",
        "pyautogui>=0.9.50",
        "moviepy>=1.0.3",
        "scipy>=1.5.0",
        "pillow>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "screen-recorder=main:main",
        ],
    },
)
