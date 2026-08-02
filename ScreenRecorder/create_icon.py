"""
Скрипт для создания иконки приложения
Запускайте: python create_icon.py
"""
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_app_icon():
    """Создание иконки приложения"""
    print("🎨 Создание иконки приложения...")

    # Создаем папку assets если её нет
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    # Создаем иконку размером 256x256
    size = 256
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)

    # Цвета
    bg_color = (30, 30, 30, 255)
    accent_color = (0, 122, 204, 255)  # #007acc
    red_color = (211, 47, 47, 255)  # #d32f2f
    white_color = (255, 255, 255, 255)

    # Рисуем круглый фон
    draw.ellipse([20, 20, size - 20, size - 20], fill=bg_color, outline=accent_color, width=4)

    # Рисуем корпус камеры
    camera_width = 160
    camera_height = 120
    camera_x = (size - camera_width) // 2
    camera_y = (size - camera_height) // 2 + 10

    # Основной корпус
    draw.rounded_rectangle(
        [camera_x, camera_y, camera_x + camera_width, camera_y + camera_height],
        radius=10,
        fill=(50, 50, 50, 255),
        outline=white_color,
        width=3
    )

    # Объектив
    lens_radius = 40
    lens_x = size // 2
    lens_y = camera_y + camera_height // 2
    draw.ellipse(
        [lens_x - lens_radius, lens_y - lens_radius,
         lens_x + lens_radius, lens_y + lens_radius],
        fill=(80, 80, 80, 255),
        outline=white_color,
        width=2
    )

    # Блик на объективе
    draw.ellipse(
        [lens_x - 15, lens_y - 15, lens_x - 5, lens_y - 5],
        fill=(200, 200, 200, 100)
    )

    # Кнопка записи
    button_radius = 25
    button_x = size - 60
    button_y = 40
    draw.ellipse(
        [button_x - button_radius, button_y - button_radius,
         button_x + button_radius, button_y + button_radius],
        fill=red_color,
        outline=white_color,
        width=2
    )

    # Вспышка
    flash_width = 20
    flash_height = 10
    flash_x = camera_x + 20
    flash_y = camera_y + 15
    draw.rounded_rectangle(
        [flash_x, flash_y, flash_x + flash_width, flash_y + flash_height],
        radius=3,
        fill=(200, 200, 200, 200)
    )

    # Сохраняем в PNG
    png_path = assets_dir / "icon.png"
    icon.save(png_path, "PNG")
    print(f"✅ PNG иконка создана: {png_path}")

    # Конвертируем в ICO
    ico_path = assets_dir / "icon.ico"

    # Создаем несколько размеров для ICO
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    icons = []

    for w, h in sizes:
        # Изменяем размер
        resized = icon.resize((w, h), Image.Resampling.LANCZOS)
        icons.append(resized)

    # Сохраняем ICO с несколькими размерами
    icons[0].save(
        ico_path,
        format='ICO',
        sizes=[(w, h) for w, h in sizes],
        append_images=icons[1:]
    )
    print(f"✅ ICO иконка создана: {ico_path}")

    # Создаем также иконку для трея (маленькая)
    tray_icon_path = assets_dir / "tray_icon.png"
    tray_size = 64
    tray_icon = icon.resize((tray_size, tray_size), Image.Resampling.LANCZOS)
    tray_icon.save(tray_icon_path, "PNG")
    print(f"✅ Иконка для трея создана: {tray_icon_path}")

    print("\n✅ Все иконки созданы успешно!")
    return ico_path


if __name__ == '__main__':
    create_app_icon()
