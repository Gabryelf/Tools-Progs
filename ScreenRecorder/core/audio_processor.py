"""
Модуль для обработки аудио и шумоподавления - максимально простая версия
"""
import numpy as np
from scipy import signal
import sounddevice as sd


class AudioProcessor:
    """Класс для обработки аудио - только фильтр высоких частот"""

    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.is_initialized = True

    def capture_noise_profile(self, duration=0.5):
        """Заглушка - не используется"""
        print("✅ Шумоподавление: фильтр высоких частот")
        return True

    def apply_highpass_filter(self, audio_data, cutoff_freq=100):
        """
        Простой фильтр высоких частот
        Убирает низкочастотный гул, сохраняет речь
        """
        try:
            nyquist = self.sample_rate / 2
            normalized_cutoff = cutoff_freq / nyquist

            if normalized_cutoff >= 1.0 or normalized_cutoff <= 0:
                return audio_data

            # Фильтр 2-го порядка - хороший баланс
            b, a = signal.butter(2, normalized_cutoff, btype='high')

            # Применяем фильтр
            if len(audio_data.shape) == 1:
                return signal.filtfilt(b, a, audio_data)
            else:
                filtered = np.zeros_like(audio_data)
                for channel in range(audio_data.shape[1]):
                    filtered[:, channel] = signal.filtfilt(b, a, audio_data[:, channel])
                return filtered

        except Exception as e:
            print(f"⚠️ Ошибка применения фильтра: {e}")
            return audio_data
