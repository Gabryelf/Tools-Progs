# ROADMAP.md — Task Manager

---

# Task Manager — план реализации

## Версия → Задача

---

### ![v0.0.1](https://img.shields.io/badge/version-0.0.1-blue) — Базовый каркас

- [ ] создать цикл приложения и список задач
- [ ] создать добавление задачи
- [ ] создать просмотр всех задач

---

### ![v0.0.2](https://img.shields.io/badge/version-0.0.2-blue) — Выход и сохранение

- [ ] создать выход из приложения
- [ ] создать сохранение заметок в список
- [ ] обеспечить обработку неверного пункта

---

### ![v0.0.3](https://img.shields.io/badge/version-0.0.3-blue) — Контент задачи

- [ ] реализовать контент заметки при добавлении
- [ ] исправить показ заметок по названию
- [ ] сделать удобным просмотр заметок и контента по отдельности

---

### ![v0.0.4](https://img.shields.io/badge/version-0.0.4-blue) — Редактирование

- [ ] экран редактирования (имя + содержание)
- [ ] сохранение изменений в файл
- [ ] возврат на список после сохранения

---

### ![v0.0.5](https://img.shields.io/badge/version-0.0.5-blue) — Удаление и подтверждение

- [ ] кнопка «Удалить» у задачи
- [ ] подтверждение с показом имени
- [ ] исправить `utils.check_confirm`
- [ ] исправить `core.deleated_task`

---

### ![v0.0.6](https://img.shields.io/badge/version-0.0.6-blue) — Поиск

- [ ] экран поиска
- [ ] поиск без учёта регистра
- [ ] отфильтрованный список через `show_tasks`
- [ ] сообщение «ничего не найдено»

---

### ![v0.0.7](https://img.shields.io/badge/version-0.0.7-blue) — Модульный UI

- [ ] `ui/ui.py` — только запуск
- [ ] `ui/screens.py` — экраны
- [ ] `ui/state.py` — глобальное состояние
- [ ] никаких циклических импортов

---

### ![v0.0.8](https://img.shields.io/badge/version-0.0.8-blue) — Консоль ↔ GUI

- [ ] выбор режима при запуске в `main.py`
- [ ] единый `saves.txt` для обеих версий
- [ ] тест переключения

---

### ![v0.0.9](https://img.shields.io/badge/version-0.0.9-blue) — Сервисный слой

- [ ] `service.py`: `add_task`, `edit_task`, `delete_task`
- [ ] `core.py` использует `service.py`
- [ ] `ui/screens.py` использует `service.py`
- [ ] нет дублирования логики

---

### ![v0.1.0](https://img.shields.io/badge/version-0.1.0-green) — Структура задачи

- [ ] формат хранения `имя | содержание`
- [ ] `load_collection` возвращает `dict`
- [ ] `save_collection` пишет `dict`
- [ ] миграция старого `saves.txt`

---

### ![v0.1.1](https://img.shields.io/badge/version-0.1.1-green) — `AppButton` везде

- [ ] класс `AppButton` наследует `tk.Button`
- [ ] `super().__init__` обязателен
- [ ] заменить все `tk.Button` на `AppButton`
- [ ] дефолты: `width=16`, `height=1`, `bg="#333333"`

---

### ![v0.1.2](https://img.shields.io/badge/version-0.1.2-green) — Варианты кнопок

- [ ] `PrimaryButton` — синий
- [ ] `DangerButton` — красный
- [ ] `SmallButton` — компактный
- [ ] заменить по смыслу в `screens.py`

---

### ![v0.1.3](https://img.shields.io/badge/version-0.1.3-orange) — Кастомные виджеты как стандарт

- [ ] `AppButton`, `AppLabel`, `AppEntry`, `AppFrame`
- [ ] правило: виджеты только через эти классы
- [ ] `ui/Button.py` → `ui/widgets.py`
- [ ] обновить `main.py` до `0.1.3`
- [ ] поиск по проекту: `tk.Button(` — только в `widgets.py`

---

