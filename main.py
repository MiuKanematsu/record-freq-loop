import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import time
import pandas as pd
from datetime import datetime

duration = 30  # 30秒間録音する
high_freq_threshold = 30000  # 高周波のしきい値

# デバイス確認
sd.default.device = [0, 0]  # Input, Outputデバイス指定
device_list = sd.query_devices()
print(device_list)

# デバイス情報関連
input_device_info = sd.query_devices(device=sd.default.device[0])
sr_in = int(input_device_info["default_samplerate"])
print(f"Sampling Rate: {sr_in} Hz")


def check_high_freq(data):
    """高周波が含まれているか確認する関数"""
    # FFTを適用して振幅スペクトルを計算
    fft_result = np.fft.fft(data)
    freq = np.fft.fftfreq(len(fft_result), 1/sr_in)
    # 高周波が含まれているか
    high_freqs = np.abs(fft_result[freq >= high_freq_threshold])
    # 閾値調整のための関数
    # np.min(high_freqs)
    # np.max(high_freqs)
    # np.mean(high_freqs)
    # np.median(high_freqs)
    np.sort(high_freqs)[::-1]
    # return np.any(high_freqs > 10)  # 振幅のしきい値を設定
    return high_freqs

csv_file = 'high_freqs_log.csv'
# CSVファイルの初期化
if not os.path.exists(csv_file):
    with open(csv_file, 'w') as f:
        f.write('timestamp,channel,high_freqs_min,high_freqs_max,high_freqs_mean,high_freqs_median\n')

while True:
    # 録音
    print("Recording Start")
    myrecording = sd.rec(int(duration * sr_in), samplerate=sr_in, channels=2)
    # ret = sd.wait(ignore_errors=False, timeout=duration)

    ret = sd.wait(ignore_errors=False)
    if ret is not None:
        print('error: ', ret.input_overflow, ret.input_underflow)
        continue
    else:
        print("not error")

    timestamp = str(datetime.now())

    # 高周波のチェックとファイルの保存
    for channel in range(2):
        high_freqs = check_high_freq(myrecording[:, channel])
        high_freq_detected = np.any(high_freqs > 30)  # 高周波が検出されたか

        if high_freq_detected:
            output_filename = f"myrecording_{timestamp}_{channel}.wav"
            sf.write(output_filename, myrecording[:, channel], sr_in)
            print(f"File saved as: {output_filename}")
        else:
            print(f"{timestamp}: No high frequencies detected in channel {channel}. File not saved.")

        high_freqs_min = np.min(high_freqs) if len(high_freqs) > 0 else 0
        high_freqs_max = np.max(high_freqs) if len(high_freqs) > 0 else 0
        high_freqs_mean = np.mean(high_freqs) if len(high_freqs) > 0 else 0
        high_freqs_median = np.median(high_freqs) if len(high_freqs) > 0 else 0

        # 高周波の値をCSVに追記
        with open(csv_file, 'a') as f:
            f.write(
                f"{timestamp},{channel},{high_freqs_min},{high_freqs_max},{high_freqs_mean},{high_freqs_median}\n")

    # # 高周波のチェック
    # if check_high_freq(myrecording[:, 0]):
    #     output_filename = f"myrecording_{timestamp}_0.wav"
    #     sf.write(output_filename, myrecording[:, 0], sr_in)
    #     print(f"File saved as: {output_filename}")
    # else:
    #     print(f"{timestamp}: No high frequencies detected. File not saved.")
    # # 高周波の値をCSVに追記
    # high_freqs_str = ','.join(map(str, check_high_freq(myrecording[:, 0])))
    # with open(csv_file, 'a') as f:
    #     f.write(f"{timestamp},0,{high_freqs_str}\n")
    #
    # if check_high_freq(myrecording[:, 1]):
    #     output_filename = f"myrecording_{timestamp}_1.wav"
    #     sf.write(output_filename, myrecording[:, 1], sr_in)
    #     print(f"File saved as: {output_filename}")
    # else:
    #     print(f"{timestamp}: No high frequencies detected. File not saved.")
    # # 高周波の値をCSVに追記
    # high_freqs_str = ','.join(map(str, check_high_freq(myrecording[:, 1])))
    # with open(csv_file, 'a') as f:
    #     f.write(f"{timestamp},1,{high_freqs_str}\n")