import os
import time
import json
import signal
from itertools import product
from multiprocessing import Pool
from typing import Tuple, List, Generator, Dict
from collections import defaultdict, namedtuple

import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


os.environ['SPOTIPY_CLIENT_ID'] = 'aeeb130410d246f0bb6ac236463f69b9'
os.environ['SPOTIPY_CLIENT_SECRET'] = '167cdf2b758f44ddbf5aad6f25c262ea'


START = 0
END = 1000
STEP, LIMIT = 50, 50


def crawl_tracks(args):
    api = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    genre, offset = args
    tracks = []
    query = api.search(f'genre: {genre}', limit = LIMIT, offset=offset, type='track', market=None)

    for track in query['tracks']['items']:
        tracks.append({
            'id': track['id'],
            'artist': track['artists'][0]['name'],
            'title': track['name'],
            'preview': track['preview_url']
        })
    time.sleep(1)
    print(f'{genre} {offset}')
    return {'genre': genre, 'tracks': tuple(tracks)}


if __name__ == '__main__':
    """
    Note to self: Did small hack here, instead of downloading meta about all
    songs, I retried for certain genres only
    """
    # spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    # genres = spotify.recommendation_genre_seeds()['genres']
    genres = ['bossanova']
    db = defaultdict(list)

    with open('data.json', 'r', encoding='utf-8') as f:
        # Note: Hack above led to modifications in this block
        cached = json.load(f)
        for k, v in cached.items():
            db[k] = v

    for genre in genres:
        # Note: Hack above led to modifications in this block
        try:
            del db[genre]
        except KeyError:
            continue

    for offset in range(START, END, STEP):
        pool = Pool(processes=8)
        arg_list = list(product(genres, [offset]))
        results = pool.map(crawl_tracks, arg_list)

        for result in results:
            db[result['genre']].extend(list(result['tracks']))

        print(f'OFFSET {offset} COMPLETE')

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

    print('DONE')
    os.kill(os.getpid(), signal.CTRL_C_EVENT)
