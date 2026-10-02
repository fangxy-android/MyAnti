"""8-bit retro sound synthesizer and sound effect player."""
import math
import struct
import io
import wave
import threading
import sys

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

from config import cfg

class RetroSoundFX:
    def __init__(self):
        self._cache = {}
        self.generate_all_sounds()

    def _generate_wav(self, duration_s: float, freq_func, sample_rate: int = 22050, volume: float = 0.5) -> bytes:
        total_samples = int(sample_rate * duration_s)
        samples = []
        phase = 0.0

        for i in range(total_samples):
            t = i / sample_rate
            freq = freq_func(t, duration_s)
            phase += 2.0 * math.pi * freq / sample_rate
            # 8-bit retro pulse/square wave mixed with sine for pleasant softness
            val_sine = math.sin(phase)
            val_square = 1.0 if (val_sine >= 0) else -1.0
            val = 0.6 * val_sine + 0.4 * val_square

            # Apply envelope (Attack, Decay, Release) to eliminate clicking
            decay = math.exp(-3.5 * (t / duration_s))
            fade_in = min(1.0, t * 100.0)
            sample_val = val * decay * fade_in * volume

            int_val = int(max(-32767, min(32767, sample_val * 32767)))
            samples.append(struct.pack('<h', int_val))

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(samples))

        return buffer.getvalue()

    def generate_all_sounds(self):
        # 1. Click / Pet: cute high chirp
        def chirp_freq(t, dur):
            return 520 + 700 * (t / dur)
        self._cache["click"] = self._generate_wav(0.12, chirp_freq, volume=0.35)

        # 2. Done / Success: celebratory arpeggio chime
        def done_freq(t, dur):
            progress = t / dur
            if progress < 0.25:
                return 523.25  # C5
            elif progress < 0.50:
                return 659.25  # E5
            elif progress < 0.75:
                return 783.99  # G5
            else:
                return 1046.50 # C6
        self._cache["done"] = self._generate_wav(0.40, done_freq, volume=0.45)

        # 3. Error / Alert: gentle double warning buzz
        def error_freq(t, dur):
            half = dur / 2.0
            cur = t % half
            return 220 if cur < half * 0.7 else 180
        self._cache["error"] = self._generate_wav(0.28, error_freq, volume=0.4)

        # 4. Bubble / Thinking: soft ascending water-drop
        def bubble_freq(t, dur):
            return 440 + 600 * ((t / dur) ** 2)
        self._cache["bubble"] = self._generate_wav(0.15, bubble_freq, volume=0.3)

        # 5. Notify / Message: crisp two-tone bell
        def notify_freq(t, dur):
            return 880 if (t / dur) < 0.4 else 1318.5
        self._cache["notify"] = self._generate_wav(0.22, notify_freq, volume=0.4)

        # 6. Typing / Tick: very short soft click
        def tick_freq(t, dur):
            return 800 - 400 * (t / dur)
        self._cache["tick"] = self._generate_wav(0.04, tick_freq, volume=0.2)

    def play(self, sound_name: str):
        if not cfg.get("sound_enabled", True):
            return

        sound_data = self._cache.get(sound_name)
        if not sound_data:
            return

        def _play_worker():
            try:
                if HAS_WINSOUND:
                    winsound.PlaySound(sound_data, winsound.SND_MEMORY | winsound.SND_ASYNC)
            except Exception as e:
                pass

        threading.Thread(target=_play_worker, daemon=True).start()

# Global sound instance
sound_player = RetroSoundFX()
