import sounddevice as sd
import numpy as np

DURATION = 5  # seconds
FS = 44100

def record_sound():
    print("ضبط صدا آغاز شد...")
    audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype='float64')
    sd.wait()
    print("ضبط پایان یافت")
    return audio

def analyze(audio):
    # تحلیل طیف فرکانسی برای تشخیص صدای فن
    fft = np.fft.rfft(audio.flatten())
    freqs = np.fft.rfftfreq(len(audio), 1/FS)
    peak_freq = freqs[np.argmax(np.abs(fft))]
    return peak_freq

if __name__ == "__main__":
    audio = record_sound()
    peak = analyze(audio)
    print(f"بالاترین فرکانس: {peak:.2f} Hz (محتمل برای فن یا نویز خاص)")