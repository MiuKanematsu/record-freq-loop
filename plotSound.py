import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import spectrogram

# デフォルトデバイスを指定
device_index = 0  # 使用するデバイスのインデックスを指定
sd.default.device = device_index

# サンプリング周波数を192 kHzに設定
fs = 192000  # サンプリング周波数
nperseg = 2048  # スペクトログラムのセグメント長

# 音声データ用の配列
duration = 1.0
data_length = int(fs * duration)
data = np.zeros((data_length, 2))  # ステレオ用のデータ配列

# プロットの初期設定
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
cax1 = ax1.imshow(np.zeros((nperseg // 2 + 1, 1)), aspect='auto', origin='lower', extent=[0, duration, 0, fs // 2],
                  cmap='plasma')
cax2 = ax2.imshow(np.zeros((nperseg // 2 + 1, 1)), aspect='auto', origin='lower', extent=[0, duration, 0, fs // 2],
                  cmap='plasma')

ax1.set_title("Left Channel Spectrogram")
ax2.set_title("Right Channel Spectrogram")
ax1.set_ylabel("Frequency (Hz)")
ax2.set_ylabel("Frequency (Hz)")
ax2.set_xlabel("Time (s)")


def callback(indata, frames, time, status):
    global data
    data = np.roll(data, -frames, axis=0)
    data[-frames:] = indata
    print(data[-10:])  # 直近のデータを印刷して確認


def update_plot(frame):
    global data
    f_left, t_left, Sxx_left = spectrogram(data[:, 0], fs, nperseg=nperseg)
    f_right, t_right, Sxx_right = spectrogram(data[:, 1], fs, nperseg=nperseg)

    cax1.set_array(Sxx_left)
    cax2.set_array(Sxx_right)

    # 最大値に基づいてスケーリングを設定
    cax1.set_clim(0, np.max(Sxx_left) if np.max(Sxx_left) > 0 else 1)
    cax2.set_clim(0, np.max(Sxx_right) if np.max(Sxx_right) > 0 else 1)

    cax1.set_extent([0, duration, 0, fs // 2])
    cax2.set_extent([0, duration, 0, fs // 2])

    return cax1, cax2


try:
    stream = sd.InputStream(
        channels=2,  # チャンネル数をここで指定
        dtype='float32',
        callback=callback,
        samplerate=fs
    )

    ani = FuncAnimation(fig, update_plot, interval=500, blit=False, cache_frame_data=False)  # 更新間隔を500msに変更

    with stream:
        plt.show()
except Exception as e:
    print(f"An error occurred: {e}")
