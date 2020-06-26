import os
from typing import Tuple
import warnings

from multiprocessing import Pool
import numpy as np
import librosa

from constants import genres


def process_song(args: Tuple[str, str]):
    warnings.filterwarnings("ignore")
    fn, genre = args
    name_no_ext = fn.split('.')[0]
    try:
        y, sr = librosa.load(f'data/{genre}/{fn}')
        x = librosa.feature.melspectrogram(y, sr)
        np.save(f'processed/{genre}/{name_no_ext}', x)
    except Exception as e:
        print(f'{e}\n===\n{fn}')


if __name__ == '__main__':
    if not os.path.exists('processed'):
        os.mkdir('processed')
        for genre in genres:
            os.mkdir(f'processed/{genre}')

    pool = Pool(6)
    file_tree = os.walk('data')
    next(file_tree)  # Skip root directory
    for root, dirs, files in file_tree:
        genre=root.split('\\')[1]
        if genre in genres:
            pool.map(process_song, [(fn, genre) for fn in files])
            pool.close()
            pool.join()
            print(f'DONE {genre}')
