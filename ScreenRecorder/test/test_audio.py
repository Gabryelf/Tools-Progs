"""
Тестовый модуль для проверки обработки аудио
"""
import sys
import os
import logging
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audio_processor import AudioProcessor
from core.settings import SettingsManager


def setup_test_logging():
    """Настройка логирования для тестов"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_audio_processor():
    """Тестирование аудио процессора"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ АУДИО ПРОЦЕССОРА")
    print("=" * 60)

    # Создаем тестовый сигнал
    sample_rate = 48000
    duration = 2.0  # секунды
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Создаем сигнал с шумом и голосом
    # 1. Низкочастотный шум (гул) - 50 Гц
    noise = 0.5 * np.sin(2 * np.pi * 50 * t)

    # 2. Голосовой сигнал (речь) - 300 Гц
    voice = 1.0 * np.sin(2 * np.pi * 300 * t)

    # 3. Смешиваем сигналы
    test_signal = noise + voice

    # Добавляем белый шум
    white_noise = 0.1 * np.random.randn(len(test_signal))
    test_signal = test_signal + white_noise

    # Сохраняем оригинальный сигнал
    original_file = "test_audio_original.wav"
    sf.write(original_file, test_signal, sample_rate)
    print(f"✅ Оригинальный сигнал сохранен: {original_file}")
    print(f"   - Частота дискретизации: {sample_rate} Гц")
    print(f"   - Длительность: {duration} сек")
    print(f"   - Амплитуда шума: {np.max(np.abs(noise)):.3f}")
    print(f"   - Амплитуда голоса: {np.max(np.abs(voice)):.3f}")

    # Инициализируем аудио процессор
    processor = AudioProcessor(sample_rate)
    print(f"\n✅ Аудио процессор инициализирован")

    # 1. Тест фильтра высоких частот
    print("\n" + "-" * 40)
    print("📊 ТЕСТ 1: ФИЛЬТР ВЫСОКИХ ЧАСТОТ")
    print("-" * 40)

    filtered_signal = processor.apply_highpass_filter(test_signal, cutoff_freq=80)
    filtered_file = "test_audio_filtered.wav"
    sf.write(filtered_file, filtered_signal, sample_rate)
    print(f"✅ Отфильтрованный сигнал сохранен: {filtered_file}")

    # Анализ результатов
    original_rms = np.sqrt(np.mean(test_signal ** 2))
    filtered_rms = np.sqrt(np.mean(filtered_signal ** 2))
    reduction = (1 - filtered_rms / original_rms) * 100

    print(f"\n📊 Результаты:")
    print(f"   - RMS оригинала: {original_rms:.4f}")
    print(f"   - RMS после фильтра: {filtered_rms:.4f}")
    print(f"   - Подавление шума: {reduction:.1f}%")

    # 2. Тест нормализации
    print("\n" + "-" * 40)
    print("📊 ТЕСТ 2: НОРМАЛИЗАЦИЯ")
    print("-" * 40)

    normalized_signal = processor.normalize(filtered_signal, target_level=0.9)
    normalized_file = "test_audio_normalized.wav"
    sf.write(normalized_file, normalized_signal, sample_rate)
    print(f"✅ Нормализованный сигнал сохранен: {normalized_file}")

    max_val = np.max(np.abs(normalized_signal))
    print(f"\n📊 Результаты:")
    print(f"   - Максимальная амплитуда: {max_val:.3f}")
    print(f"   - Целевой уровень: 0.9")
    print(f"   - Достигнутый уровень: {max_val:.3f}")

    # 3. Тест с реальным аудио (если есть микрофон)
    print("\n" + "-" * 40)
    print("📊 ТЕСТ 3: ЗАПИСЬ И ОБРАБОТКА РЕАЛЬНОГО АУДИО")
    print("-" * 40)

    try:
        print("🎤 Запись 3 секунд аудио...")
        record_duration = 3.0
        audio_data = sd.rec(
            int(sample_rate * record_duration),
            samplerate=sample_rate,
            channels=2,
            dtype='float32'
        )
        sd.wait()

        # Сохраняем оригинал
        real_original = "test_real_original.wav"
        sf.write(real_original, audio_data, sample_rate)
        print(f"✅ Оригинальная запись сохранена: {real_original}")

        # Обрабатываем
        processed_audio = processor.apply_highpass_filter(audio_data, cutoff_freq=80)
        processed_audio = processor.normalize(processed_audio)

        # Сохраняем обработанный
        real_processed = "test_real_processed.wav"
        sf.write(real_processed, processed_audio, sample_rate)
        print(f"✅ Обработанная запись сохранена: {real_processed}")

        print(f"\n📊 Результаты:")
        print(f"   - Длительность записи: {record_duration} сек")
        print(f"   - Каналов: {audio_data.shape[1]}")
        print(f"   - Размер оригинального: {os.path.getsize(real_original)} байт")
        print(f"   - Размер обработанного: {os.path.getsize(real_processed)} байт")

    except Exception as e:
        print(f"⚠️ Ошибка записи: {e}")
        print("   (Пропускаем тест с реальным аудио)")

    # 4. Тест настроек
    print("\n" + "-" * 40)
    print("📊 ТЕСТ 4: НАСТРОЙКИ")
    print("-" * 40)

    settings = SettingsManager()
    print(f"✅ Настройки загружены")
    print(f"   - Шумоподавление: {'включено' if settings.get('noise_reduction') else 'выключено'}")
    print(f"   - Частота среза: {settings.get('highpass_cutoff')} Гц")
    print(f"   - Частота дискретизации: {settings.get('audio_sample_rate')} Гц")
    print(f"   - Каналов: {settings.get('audio_channels')}")

    # Итоговый отчет
    print("\n" + "=" * 60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("=" * 60)
    print("\n📁 Сгенерированные файлы:")
    print(f"   1. {original_file} - оригинальный тестовый сигнал")
    print(f"   2. {filtered_file} - после фильтрации")
    print(f"   3. {normalized_file} - после нормализации")
    if os.path.exists("test_real_original.wav"):
        print(f"   4. test_real_original.wav - реальная запись")
        print(f"   5. test_real_processed.wav - обработанная запись")

    print("\n💡 Для прослушивания используйте любой аудиоплеер")
    print("💡 Сравните оригинал и обработанные файлы")


def test_audio_devices():
    """Тестирование аудио устройств"""
    print("\n" + "=" * 60)
    print("🎵 ДОСТУПНЫЕ АУДИО УСТРОЙСТВА")
    print("=" * 60)

    try:
        devices = sd.query_devices()

        print("\n📋 Входные устройства:")
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                print(f"   [{i}] {dev['name']}")
                print(f"       - Каналов: {dev['max_input_channels']}")
                print(f"       - Частота: {dev['default_samplerate']} Гц")

                # Проверяем loopback
                name_lower = dev['name'].lower()
                is_loopback = any(k in name_lower for k in ['loopback', 'stereo mix', 'what u hear'])
                if is_loopback:
                    print(f"       - 🔄 Loopback устройство")

        print("\n📋 Выходные устройства:")
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                print(f"   [{i}] {dev['name']}")
                print(f"       - Каналов: {dev['max_output_channels']}")

        # Устройство по умолчанию
        default_input = sd.default.device[0]
        print(f"\n🎯 Устройство по умолчанию: {default_input}")
        if default_input is not None:
            dev_info = sd.query_devices(default_input)
            print(f"   - Имя: {dev_info['name']}")
            print(f"   - Каналов входа: {dev_info['max_input_channels']}")

    except Exception as e:
        print(f"⚠️ Ошибка получения устройств: {e}")


def test_audio_quality():
    """Тестирование качества обработки аудио"""
    print("\n" + "=" * 60)
    print("📊 АНАЛИЗ КАЧЕСТВА ОБРАБОТКИ")
    print("=" * 60)

    sample_rate = 48000
    duration = 1.0

    # Создаем тестовый сигнал с известными частотами
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Частоты: 50 Гц (шум), 200 Гц (голос), 1000 Гц (высокие)
    test_signal = (
            0.5 * np.sin(2 * np.pi * 50 * t) +  # Низкие частоты (шум)
            1.0 * np.sin(2 * np.pi * 200 * t) +  # Средние частоты (голос)
            0.3 * np.sin(2 * np.pi * 1000 * t)  # Высокие частоты
    )

    processor = AudioProcessor(sample_rate)
    filtered = processor.apply_highpass_filter(test_signal, cutoff_freq=80)
    normalized = processor.normalize(filtered)

    # Спектральный анализ
    def analyze_spectrum(signal, name):
        fft = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(len(signal), 1 / sample_rate)

        # Находим амплитуды на наших частотах
        idx_50 = np.argmin(np.abs(freqs - 50))
        idx_200 = np.argmin(np.abs(freqs - 200))
        idx_1000 = np.argmin(np.abs(freqs - 1000))

        amp_50 = np.abs(fft[idx_50])
        amp_200 = np.abs(fft[idx_200])
        amp_1000 = np.abs(fft[idx_1000])

        print(f"\n{name}:")
        print(f"   - 50 Гц (шум): {amp_50:.3f}")
        print(f"   - 200 Гц (голос): {amp_200:.3f}")
        print(f"   - 1000 Гц (высокие): {amp_1000:.3f}")

        # Отношение сигнал/шум
        if amp_50 > 0.001:
            snr_200 = amp_200 / amp_50
            snr_1000 = amp_1000 / amp_50
            print(f"   - SNR 200/50: {snr_200:.1f}")
            print(f"   - SNR 1000/50: {snr_1000:.1f}")

        return amp_50, amp_200, amp_1000

    print("\n📊 Спектральный анализ:")
    print("-" * 40)

    orig_50, orig_200, orig_1000 = analyze_spectrum(test_signal, "Оригинал")
    filt_50, filt_200, filt_1000 = analyze_spectrum(filtered, "После фильтра")
    norm_50, norm_200, norm_1000 = analyze_spectrum(normalized, "После нормализации")

    # Оценка качества
    print("\n📈 Оценка качества:")
    print("-" * 40)

    if filt_50 < orig_50 * 0.3:
        print("   ✅ Низкие частоты (шум) успешно подавлены")
    else:
        print("   ⚠️ Низкие частоты подавлены недостаточно")

    if filt_200 > orig_200 * 0.7:
        print("   ✅ Средние частоты (голос) сохранены")
    else:
        print("   ⚠️ Средние частоты частично потеряны")

    if filt_1000 > orig_1000 * 0.7:
        print("   ✅ Высокие частоты сохранены")
    else:
        print("   ⚠️ Высокие частоты частично потеряны")


def main():
    """Главная функция тестирования"""
    setup_test_logging()

    print("\n" + "=" * 60)
    print("🎵 ТЕСТИРОВАНИЕ АУДИО КОМПОНЕНТОВ")
    print("=" * 60)

    # 1. Тест аудио устройств
    test_audio_devices()

    # 2. Тест аудио процессора
    test_audio_processor()

    # 3. Тест качества
    test_audio_quality()

    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 60)


if __name__ == '__main__':
    main()
