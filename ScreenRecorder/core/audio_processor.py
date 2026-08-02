"""
Модуль для обработки аудио и шумоподавления
"""
import logging
import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Класс для обработки аудио - только фильтр высоких частот

    Attributes:
        sample_rate: Частота дискретизации
        is_initialized: Флаг инициализации
    """

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self._is_initialized = True

    @property
    def is_initialized(self) -> bool:
        """Проверка инициализации"""
        return self._is_initialized

    def capture_noise_profile(self, duration: float = 0.5) -> bool:
        """
        Заглушка - не используется в упрощенной версии

        Args:
            duration: Длительность захвата

        Returns:
            Всегда True
        """
        logger.info("Шумоподавление: фильтр высоких частот")
        return True

    def apply_highpass_filter(self, audio_data: np.ndarray, cutoff_freq: int = 80) -> np.ndarray:
        """
        Простой фильтр высоких частот

        Убирает низкочастотный гул (шум кулера, гудение),
        сохраняя речь и высокие частоты.

        Args:
            audio_data: Входной аудиосигнал
            cutoff_freq: Частота среза в Гц

        Returns:
            Отфильтрованный аудиосигнал
        """
        try:
            if len(audio_data) == 0:
                return audio_data

            nyquist = self.sample_rate / 2
            normalized_cutoff = cutoff_freq / nyquist

            if not (0 < normalized_cutoff < 1.0):
                return audio_data

            # Фильтр Баттерворта 2-го порядка
            b, a = signal.butter(2, normalized_cutoff, btype='high')

            # Применение фильтра
            if len(audio_data.shape) == 1:
                return signal.filtfilt(b, a, audio_data)
            else:
                filtered = np.zeros_like(audio_data)
                for channel in range(audio_data.shape[1]):
                    filtered[:, channel] = signal.filtfilt(b, a, audio_data[:, channel])
                return filtered

        except Exception as e:
            logger.error(f"Ошибка применения фильтра: {e}")
            return audio_data

    def normalize(self, audio_data: np.ndarray, target_level: float = 0.9) -> np.ndarray:
        """
        Нормализация аудио

        Args:
            audio_data: Входной аудиосигнал
            target_level: Целевой уровень (0.0 - 1.0)

        Returns:
            Нормализованный аудиосигнал
        """
        try:
            if len(audio_data) == 0:
                return audio_data

            max_val = np.max(np.abs(audio_data))
            if max_val > 0.01:
                return audio_data / max_val * target_level
            return audio_data
        except Exception as e:
            logger.error(f"Ошибка нормализации: {e}")
            return audio_data
