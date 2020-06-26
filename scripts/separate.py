import os
import time
import shutil
import logging
from typing import Tuple, Dict
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

import librosa
import numpy as np
from spleeter.separator import Separator
from spleeter.audio.adapter import get_default_audio_adapter
from spleeter.utils.logging import get_logger


from constants import genres


def handle_song(genre: str, fn: str, sr: int=22050):
    name_no_ext = fn.split('.')[0]
    acc, _ = librosa.load(f'{name_no_ext}/accompaniment.wav')
    voc, _ = librosa.load(f'{name_no_ext}/vocals.wav')

    x_voc = librosa.feature.melspectrogram(voc, sr=sr)
    x_instr = librosa.feature.melspectrogram(acc, sr=sr)
    np.save(f'processed-instr/{genre}/{name_no_ext}', x_instr)
    np.save(f'processed-voc/{genre}/{name_no_ext}', x_voc)
    shutil.rmtree(name_no_ext)


if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=8)
    separator = Separator('spleeter:2stems')
    audio_loader = get_default_audio_adapter()

    if not os.path.exists('processed-instr'):
        os.mkdir('processed-instr')
        os.mkdir('processed-voc')
        for genre in genres:
            os.mkdir(f'processed-instr/{genre}')
            os.mkdir(f'processed-voc/{genre}')

    file_tree = os.walk('data')
    next(file_tree)  # Skip root directory
    sr = 22050
    time_in = time.perf_counter()
    for root, dirs, files in file_tree:
        # Genre loop
        idx = 0
        genre=root.split('\\')[1]
        if genre not in genres:
            continue
        for fn in files:
            # Audio clip loop
            if idx == 500:
                # Extract only 500 clips of each selected genre
                break
            waveform, _ = audio_loader.load(f'data/{genre}/{fn}', sample_rate=sr)

            separator.separate_to_file(f'data/{genre}/{fn}', '.')
            executor.submit(handle_song, genre, fn)
            idx += 1
        print(f'{genre} DONE')
    executor.shutdown()
    time_out = time.perf_counter()
    print(f'DONE {time_out - time_in:0.4f}')
