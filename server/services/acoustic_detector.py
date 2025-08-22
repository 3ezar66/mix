import sounddevice as sd
import numpy as np
from scipy.fft import fft
from typing import Optional, Dict

def detect_miner_acoustic(duration: int = 10, samplerate: int = 44100) -> Optional[Dict]:
    """
    تحلیل صوتی محیط برای شناسایی صدای فن یا نویز خاص دستگاه‌های ماینر
    نیازمند میکروفون متصل به سیستم
    """
    try:
        print("در حال ضبط صدا...")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float64')
        sd.wait()
        print("تحلیل فرکانسی...")
        spectrum = np.abs(fft(audio[:,0]))
        freqs = np.fft.fftfreq(len(spectrum), 1/samplerate)
        # نمونه ساده: بررسی وجود پیک در بازه فرکانسی فن ماینرها (مثلاً 4000-8000 هرتز)
        miner_band = (freqs > 4000) & (freqs < 8000)
        peak = np.max(spectrum[miner_band])
        return {"peak": float(peak), "detected": peak > 100}
    except Exception as e:
        return {"error": str(e)}

# مثال استفاده
if __name__ == "__main__":
    print(detect_miner_acoustic())
