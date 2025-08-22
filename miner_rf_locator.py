import numpy as np
from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import time

# فرکانس‌های تقریبی دستگاه‌های ماینر (مثلاً فرکانس سوییچینگ منبع تغذیه، فن، و نویز خاص چیپ)
MINER_FREQS = [
    50e6,  # مثال: 50 MHz (با توجه به نوع منبع تغذیه سوئیچینگ)
    100e6, # مثال: 100 MHz
    432e6, # مثال: 432 MHz (UHF harmonics)
    # فرکانس دقیق بر اساس مدل دستگاه استخراج شود!
]

FREQ_BANDWIDTH = 1e6  # پهنای باند جستجو هر نقطه (1 MHz)
SAMPLES = 256*1024    # تعداد نمونه‌گیری برای هر اسکن

def scan_rf(freqs, bandwidth, samples):
    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6  # نرخ نمونه‌گیری (بسته به دانگل)
    sdr.gain = 'auto'
    results = []

    for f in freqs:
        sdr.center_freq = f
        print(f"🔍 Scanning {f/1e6:.1f} MHz ...")
        iq_samples = sdr.read_samples(samples)
        power = np.abs(np.fft.fft(iq_samples))**2
        freqs_axis = np.fft.fftfreq(len(power), 1/sdr.sample_rate) + f
        # حذف نویز عمومی: فقط قله‌های sharp و پایدار را نگه دار
        threshold = np.percentile(power, 99) * 5  # فقط قله‌های قوی‌تر
        peaks = np.where(power > threshold)[0]
        # اگر قله‌ای با شکل و قدرت خاص وجود داشت، ثبت کن
        for p in peaks:
            freq_peak = freqs_axis[p]
            results.append((freq_peak, power[p]))
            print(f"  ⚡ Detected peak at {freq_peak/1e6:.3f} MHz (Power={power[p]:.2f})")
        time.sleep(0.5)
    sdr.close()
    return results

def main():
    print("🚀 RF Miner Locator – کشف فرکانس خاص ماینر")
    results = scan_rf(MINER_FREQS, FREQ_BANDWIDTH, SAMPLES)
    # نمایش روی نمودار
    if results:
        freqs, pwr = zip(*results)
        plt.figure(figsize=(10,4))
        plt.scatter([f/1e6 for f in freqs], pwr)
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("Power")
        plt.title("Detected RF Peaks (Miner Candidates)")
        plt.grid()
        plt.show()
        # هدایت کاربر: هرچه قدرت بالاتر، نزدیک‌تر شدی!
        print("\n👣 برای مکان‌یابی دقیق: با گیرنده حرکت کن، هرچه قدرت بیشتر، نزدیک‌تر به منبع ماینر.")
    else:
        print("هیچ سیگنال خاص ماینری در این محدوده پیدا نشد.")

if __name__ == "__main__":
    main()