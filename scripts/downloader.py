import os
import json
import signal
from typing import Dict
from multiprocessing import Pool
from urllib.request import urlretrieve


Track = Dict[str, str]


def download_preview(track: Track):
    name, genre, url = track['id'], track['genre'], track['preview']
    dest_dir_path = f'data/{genre}'
    try:
        urlretrieve(url, dest_dir_path + f'/{name}.mp3')
        print(f"Done {genre} {name}")
    except TypeError:
        print(f'ERROR {url} {id}')
    finally:
        return None


# Note to self: Did small hack here, instead of downloading meta about all
# songs, I retried for certain genres only
db = {}
genres = ['bossanova']

with open('data.json', 'r', encoding='utf-8') as f:
    # Note: Hack above led to modifications in this block
    cached = json.load(f)
    for genre in genres:
        db[genre] = cached[genre]

if not os.path.exists('data'):
    os.mkdir('data')
for k in db.keys():
    genre_path = f'data/{k}'
    if not os.path.exists(genre_path):
        os.mkdir(genre_path)

tasks = []
for k, v in db.items():
    for track in v:
        partial = dict(track)
        partial['genre'] = k
        tasks.append(partial)


if __name__ == '__main__':
    pool = Pool(processes=8)
    pool.map(download_preview, tasks)

    print('DONE')
    os.kill(os.getpid(), signal.CTRL_C_EVENT)
