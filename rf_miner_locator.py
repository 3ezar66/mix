import numpy as np
from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import time

# فرکانس‌های شناخته‌شده بر اساس مدل ماینر (مثلاً هارمونیک‌های منبع تغذیه)
MINER_FREQS = [
    50e6,    # 50 MHz
    100e6,   # 100 MHz
    432e6,   # 432 MHz
    860e6,   # 860 MHz
    915e6    # 915 MHz
]

FREQ_BANDWIDTH = 2.4e6  # پهنای باند بررسی (2.4 MHz)
SAMPLES = 256*1024      # تعداد نمونه‌گیری

def scan_rf(freqs, bandwidth, samples):
    sdr = RtlSdr()
    sdr.sample_rate = bandwidth
    sdr.gain = 'auto'
    results = []

    for f in freqs:
        sdr.center_freq = f
        print(f"🔍 اسکن {f/1e6:.1f} MHz ...")
        iq_samples = sdr.read_samples(samples)
        spectrum = np.abs(np.fft.fft(iq_samples))**2
        freqs_axis = np.fft.fftfreq(len(spectrum), 1/sdr.sample_rate) + f
        # حذف نویز عمومی: فقط قله‌های sharp و پایدار
        threshold = np.percentile(spectrum, 99) * 4
        peak_idxs = np.where(spectrum > threshold)[0]
        for p in peak_idxs:
            freq_peak = freqs_axis[p]
            power = spectrum[p]
            results.append((freq_peak, power))
            print(f"  ⚡ Peak: {freq_peak/1e6:.3f} MHz, Power={power:.2f}")
        time.sleep(0.5)
    sdr.close()
    return results

def main():
    print("🚀 RF Miner Locator")
    results = scan_rf(MINER_FREQS, FREQ_BANDWIDTH, SAMPLES)
    if results:
        freqs, pwr = zip(*results)
        plt.figure(figsize=(10,4))
        plt.scatter([f/1e6 for f in freqs], pwr)
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("Power")
        plt.title("Detected RF Peaks (Miner Candidates)")
        plt.grid()
        plt.show()
        print("\n👣 برای مکان‌یابی: نزدیک‌تر شو، قدرت سیگنال بیشتر = نزدیک‌تر به دستگاه.")
    else:
        print("سیگنال خاص ماینری پیدا نشد.")

if __name__ == "__main__":
    main()