"""
Простой рендерер SVG без CairoSVG
Использует Pillow для создания изображений из SVG
"""

import re
import io
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from PIL import Image, ImageDraw, ImageTk


class SimpleSVGRenderer:
    """Простой рендерер SVG без внешних зависимостей"""

    # Кэш для уже отрендеренных иконок
    _cache = {}

    @classmethod
    def render_svg(cls, svg_path: Path, size: Tuple[int, int] = (24, 24)) -> Optional[ImageTk.PhotoImage]:
        """
        Рендеринг SVG в PhotoImage

        Args:
            svg_path: Путь к SVG файлу
            size: Размер выходного изображения (width, height)

        Returns:
            PhotoImage или None
        """
        cache_key = f"{svg_path}_{size[0]}_{size[1]}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            # Парсим SVG
            image = cls._parse_svg(svg_content, size)

            if image:
                photo = ImageTk.PhotoImage(image)
                cls._cache[cache_key] = photo
                return photo

        except Exception as e:
            print(f"⚠️ Ошибка рендеринга SVG {svg_path.name}: {e}")

        return None

    @classmethod
    def _parse_svg(cls, svg_content: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """
        Парсинг SVG и создание изображения

        Args:
            svg_content: Содержимое SVG файла
            size: Размер выходного изображения

        Returns:
            Image или None
        """
        try:
            # Создаем пустое изображение с прозрачным фоном
            img = Image.new('RGBA', size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # Извлекаем viewBox или используем размеры
            viewbox = cls._extract_viewbox(svg_content)
            if not viewbox:
                viewbox = (0, 0, 24, 24)  # Стандартный размер

            # Вычисляем масштаб для центрирования
            svg_width = viewbox[2] - viewbox[0]
            svg_height = viewbox[3] - viewbox[1]

            # Масштабируем с сохранением пропорций
            scale_x = size[0] / svg_width if svg_width > 0 else 1
            scale_y = size[1] / svg_height if svg_height > 0 else 1
            scale = min(scale_x, scale_y) * 0.85  # 85% от размера

            # Смещение для центрирования
            offset_x = (size[0] - svg_width * scale) / 2
            offset_y = (size[1] - svg_height * scale) / 2

            # Извлекаем все элементы
            elements = cls._extract_all_elements(svg_content)

            # Рисуем элементы
            for element in elements:
                cls._draw_element(draw, element, viewbox, scale, offset_x, offset_y)

            # Если нет элементов, рисуем иконку по умолчанию
            if not elements:
                cls._draw_default_icon(draw, size, '#2196F3')

            return img

        except Exception as e:
            print(f"⚠️ Ошибка парсинга SVG: {e}")
            return None

    @classmethod
    def _extract_viewbox(cls, svg_content: str) -> Optional[Tuple[float, float, float, float]]:
        """Извлечение viewBox из SVG"""
        match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_content, re.IGNORECASE)
        if match:
            parts = list(map(float, match.group(1).split()))
            if len(parts) == 4:
                return tuple(parts)

        # Пробуем извлечь ширину и высоту
        width_match = re.search(r'width=["\'](\d+)["\']', svg_content, re.IGNORECASE)
        height_match = re.search(r'height=["\'](\d+)["\']', svg_content, re.IGNORECASE)

        if width_match and height_match:
            return (0, 0, float(width_match.group(1)), float(height_match.group(1)))

        return None

    @classmethod
    def _extract_all_elements(cls, svg_content: str) -> List[Dict]:
        """Извлечение всех элементов из SVG"""
        elements = []

        # Извлекаем path элементы
        path_matches = re.findall(
            r'<path([^>]*)d=["\']([^"\']+)["\']([^>]*)/?>',
            svg_content,
            re.IGNORECASE | re.DOTALL
        )
        for attrs1, d, attrs2 in path_matches:
            element = {
                'type': 'path',
                'd': d,
                'attrs': cls._parse_attributes(attrs1 + ' ' + attrs2)
            }
            elements.append(element)

        # Извлекаем circle элементы
        circle_matches = re.findall(
            r'<circle([^>]*)/?>',
            svg_content,
            re.IGNORECASE | re.DOTALL
        )
        for attrs in circle_matches:
            parsed = cls._parse_attributes(attrs)
            if 'cx' in parsed and 'cy' in parsed and 'r' in parsed:
                element = {
                    'type': 'circle',
                    'attrs': parsed
                }
                elements.append(element)

        # Извлекаем rect элементы
        rect_matches = re.findall(
            r'<rect([^>]*)/?>',
            svg_content,
            re.IGNORECASE | re.DOTALL
        )
        for attrs in rect_matches:
            parsed = cls._parse_attributes(attrs)
            if 'x' in parsed and 'y' in parsed and 'width' in parsed and 'height' in parsed:
                element = {
                    'type': 'rect',
                    'attrs': parsed
                }
                elements.append(element)

        # Извлекаем polyline/polygon элементы
        poly_matches = re.findall(
            r'<poly(?:line|gon)([^>]*)/?>',
            svg_content,
            re.IGNORECASE | re.DOTALL
        )
        for attrs in poly_matches:
            parsed = cls._parse_attributes(attrs)
            if 'points' in parsed:
                element = {
                    'type': 'polygon',
                    'attrs': parsed
                }
                elements.append(element)

        return elements

    @classmethod
    def _parse_attributes(cls, attrs_str: str) -> Dict[str, str]:
        """Парсинг атрибутов элемента"""
        attrs = {}

        # Ищем атрибуты в формате key="value"
        attr_matches = re.findall(r'(\w+)=["\']([^"\']+)["\']', attrs_str, re.IGNORECASE)
        for key, value in attr_matches:
            attrs[key.lower()] = value

        # Ищем атрибуты в style
        if 'style' in attrs:
            style_parts = attrs['style'].split(';')
            for part in style_parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    attrs[key.strip().lower()] = value.strip()

        return attrs

    @classmethod
    def _get_color(cls, attrs: Dict, attr_name: str, default: str = '#2196F3') -> str:
        """Получение цвета из атрибутов"""
        color = attrs.get(attr_name, default)
        if color in ['none', 'transparent']:
            return None
        return color

    @classmethod
    def _draw_element(cls, draw: ImageDraw, element: Dict, viewbox: Tuple,
                      scale: float, offset_x: float, offset_y: float):
        """Рисование элемента"""
        attrs = element.get('attrs', {})
        elem_type = element.get('type', '')

        # Получаем цвета
        fill = cls._get_color(attrs, 'fill', '#2196F3')
        stroke = cls._get_color(attrs, 'stroke', None)
        stroke_width = float(attrs.get('stroke-width', 1))

        # Функция для трансформации координат
        def transform(x, y):
            return (int(x * scale + offset_x), int(y * scale + offset_y))

        def transform_size(w, h):
            return (int(w * scale), int(h * scale))

        if elem_type == 'path':
            # Рисуем path
            points = cls._parse_path_data(
                element.get('d', ''),
                viewbox, scale, offset_x, offset_y
            )
            if points and len(points) > 1:
                # Используем fill если есть
                if fill:
                    draw.polygon(points, fill=fill, outline=stroke, width=int(stroke_width))
                else:
                    draw.line(points, fill=stroke or '#2196F3', width=int(stroke_width))

        elif elem_type == 'circle':
            cx = float(attrs.get('cx', 0))
            cy = float(attrs.get('cy', 0))
            r = float(attrs.get('r', 10))

            x, y = transform(cx, cy)
            r = int(r * scale)

            draw.ellipse(
                [x - r, y - r, x + r, y + r],
                fill=fill,
                outline=stroke,
                width=int(stroke_width)
            )

        elif elem_type == 'rect':
            x = float(attrs.get('x', 0))
            y = float(attrs.get('y', 0))
            w = float(attrs.get('width', 10))
            h = float(attrs.get('height', 10))

            x1, y1 = transform(x, y)
            w, h = transform_size(w, h)

            draw.rectangle(
                [x1, y1, x1 + w, y1 + h],
                fill=fill,
                outline=stroke,
                width=int(stroke_width)
            )

        elif elem_type == 'polygon':
            points_str = attrs.get('points', '')
            points = []
            for pair in points_str.split():
                if ',' in pair:
                    x, y = pair.split(',')
                    points.append(transform(float(x), float(y)))

            if points and len(points) > 2:
                draw.polygon(points, fill=fill, outline=stroke, width=int(stroke_width))

    @classmethod
    def _parse_path_data(cls, path_data: str, viewbox: Tuple, scale: float,
                         offset_x: float, offset_y: float) -> List[Tuple[int, int]]:
        """Парсинг path данных в точки"""
        points = []

        # Разбиваем path_data на команды и координаты
        parts = re.findall(r'[A-Za-z]|[-+]?\d*\.?\d+', path_data)

        i = 0
        current_x = 0
        current_y = 0
        start_x = 0
        start_y = 0

        def add_point(x, y):
            points.append((int(x * scale + offset_x), int(y * scale + offset_y)))

        while i < len(parts):
            cmd = parts[i]
            i += 1

            if cmd in ['M', 'm', 'L', 'l']:
                # Получаем координаты
                coords = []
                while i < len(parts) and not parts[i].isalpha():
                    coords.append(float(parts[i]))
                    i += 1

                for j in range(0, len(coords) - 1, 2):
                    if j + 1 < len(coords):
                        x = coords[j]
                        y = coords[j + 1]
                        if cmd in ['m', 'l']:
                            x += current_x
                            y += current_y

                        add_point(x, y)
                        current_x = x
                        current_y = y

                        if cmd in ['M', 'm']:
                            start_x = x
                            start_y = y

            elif cmd in ['Z', 'z']:
                if points:
                    add_point(start_x, start_y)
                    current_x = start_x
                    current_y = start_y

            elif cmd in ['H', 'h']:
                while i < len(parts) and not parts[i].isalpha():
                    x = float(parts[i])
                    i += 1
                    if cmd == 'h':
                        x += current_x
                    current_x = x
                    add_point(current_x, current_y)

            elif cmd in ['V', 'v']:
                while i < len(parts) and not parts[i].isalpha():
                    y = float(parts[i])
                    i += 1
                    if cmd == 'v':
                        y += current_y
                    current_y = y
                    add_point(current_x, current_y)

            else:
                # Пропускаем другие команды
                while i < len(parts) and not parts[i].isalpha():
                    i += 1

        return points

    @classmethod
    def _draw_default_icon(cls, draw: ImageDraw, size: Tuple[int, int], color: str):
        """Рисование иконки по умолчанию"""
        w, h = size
        margin = 4

        # Рисуем простую геометрическую фигуру
        center_x = w // 2
        center_y = h // 2
        r = min(w, h) // 2 - margin

        # Квадрат с заливкой
        draw.rectangle(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            fill=color,
            outline=color,
            width=1
        )

        # Буква в центре
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", int(h * 0.5))
            draw.text((center_x - 6, center_y - 8), "S", fill='white', font=font)
        except:
            draw.text((center_x - 4, center_y - 6), "S", fill='white')


class IconManagerWithSVG:
    """Менеджер иконок с поддержкой SVG через SimpleSVGRenderer"""

    _cache = {}

    @classmethod
    def load_icon(cls, path: Path, size: Tuple[int, int] = (24, 24)):
        """
        Загрузка иконки с поддержкой SVG

        Args:
            path: Путь к иконке
            size: Размер иконки

        Returns:
            PhotoImage или None
        """
        cache_key = f"{path}_{size[0]}_{size[1]}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        if not path.exists():
            return None

        try:
            ext = path.suffix.lower()

            if ext == '.svg':
                # Используем SimpleSVGRenderer для SVG
                photo = SimpleSVGRenderer.render_svg(path, size)
            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']:
                # Загружаем растровое изображение
                image = Image.open(path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
            else:
                return None

            if photo:
                cls._cache[cache_key] = photo
                return photo

        except Exception as e:
            print(f"⚠️ Ошибка загрузки {path.name}: {e}")

        return None

    @classmethod
    def clear_cache(cls):
        """Очистка кэша"""
        cls._cache.clear()
