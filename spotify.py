import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import csv
from pathlib import Path
from datetime import datetime

cid = 'a6e40993b6c44179a59a4274e8f07852' #Client ID
secret = 'cfc0eb19c5aa4737bb73fee57a8248e7' #Client Secret
downloads_path = str(Path.home() / "Downloads")

dream_theater = 'https://open.spotify.com/artist/2aaLAng2L2aWD2FClzwiep?si=5YAksQJARP-LBCaAzswR3A'

#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def search_artist(query):
    resp = sp.search(q=query, limit=1 ,type='artist')
    uri = resp['artists']['items'][0]['uri']
    return uri

def get_artist_stats(uri):
    artist = sp.artist(uri)
    return artist

def get_top10_tracks(uri):
    top10_tracks = sp.artist_top_tracks(artist_id=uri, country='IE')
    return top10_tracks

def create_csv_name(artist):
    csv_name = artist['name']
    return csv_name

def ms_to_duration(ms):
    duration = datetime.fromtimestamp(ms/1000.0).strftime('%H:%M:%S')
    return duration

def create_artist_csv(artist, csv_name):

    fieldnames = ['id', 'name', 'popularity', 'followers']

    id = artist['id']
    name = artist['name']
    popularity = int(artist['popularity'])
    followers = int(artist['followers']['total'])

    data = dict(
    id = id,
    name = name,
    popularity = popularity,
    followers = followers)

    genres = artist['genres']

    for i in range(len(genres)):
        genre = genres[i]
        data[f'genre_{i+1}'] = genre
        fieldnames.append(f'genre_{i+1}')

    data['uri'] = artist['uri']
    fieldnames.append('uri')

    with open(f'{downloads_path}\{csv_name} Stats.csv', 'w', newline='') as csvfile:
            csv.DictWriter(csvfile, fieldnames=fieldnames).writeheader()             
            csv.writer(csvfile).writerow(list(data.values()))

    return data

def create_top10_tracks_csv(top10_tracks, csv_name):

    tracks = []

    fieldnames = ['id', 'name', 'popularity', 'duration', 
                'artist_id', 'release_date', 'album', 'uri']

    for i in range(len(top10_tracks['tracks'])):

        id = top10_tracks['tracks'][i]['id']
        name = top10_tracks['tracks'][i]['name']
        popularity = int(top10_tracks['tracks'][i]['popularity'])
        duration = int(top10_tracks['tracks'][i]['duration_ms'])
        duration = ms_to_duration(duration)
        artist_id = top10_tracks['tracks'][i]['artists'][0]['id']
        release_date = top10_tracks['tracks'][i]['album']['release_date']
        album = top10_tracks['tracks'][i]['album']['name']
        uri = top10_tracks['tracks'][i]['uri']

        data = dict(
        id = id,
        name = name,
        popularity = popularity,
        duration = duration,
        artist_id = artist_id,
        release_date = release_date,
        album = album,
        uri = uri)

        tracks.append(data)

    with open(f'{downloads_path}\{csv_name} Top10 Tracks.csv', 'w', newline='') as csvfile:
            csv.DictWriter(csvfile, fieldnames=fieldnames).writeheader()           
            for track in tracks:
                csv.writer(csvfile).writerow(list(track.values()))

    return data
