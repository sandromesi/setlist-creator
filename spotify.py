import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import csv
from pathlib import Path
import datetime
import os

cid = os.getenv('CLIENT_ID')
secret = os.getenv('CLIENT_SECRET')
#downloads_path = str(Path.home() / "Downloads")
dream_theater = 'https://open.spotify.com/artist/2aaLAng2L2aWD2FClzwiep?si=5YAksQJARP-LBCaAzswR3A'

artist_list = ['Dream Theater', 'Avenged Sevenfold', 'TOOL', 'System Of A Down', 'Slipknot', 'Bring Me The Horizon']
country = 'IE'

#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def string_to_list(query):
    artist_list = query.splitlines()
    return artist_list

def search_artist(query):
    resp = sp.search(q=query, limit=1 ,type='artist')
    uri = resp['artists']['items'][0]['uri']
    return uri

def get_artist_stats(uri):
    artist = sp.artist(uri)
    return artist

def get_top10_tracks(uri, country):
    top10_tracks = sp.artist_top_tracks(artist_id=uri, country=country)
    return top10_tracks

def create_csv_name(artist):
    csv_name = artist['name']
    return csv_name

def ms_to_duration(ms):
    duration = datetime.datetime.fromtimestamp(ms/1000.0).strftime('%H:%M:%S')
    return duration

def str_to_timedelta(str):
    time = datetime.timedelta(hours=float(str[:2]), 
    minutes=float(str[3:5]), seconds=float(str[6:8]))
    return time

def artists_to_dataframe(artist_list):

    id_list = []
    name_list = []
    followers_list = []
    popularity_list = []
    uri_list = []

    for query in artist_list:
        uri = search_artist(query)
        artist = get_artist_stats(uri)

        id = artist['id']
        name = artist['name']
        followers = int(artist['followers']['total'])
        popularity = int(artist['popularity'])
        uri = artist['uri']

        id_list.append(id)
        name_list.append(name)
        followers_list.append(followers)
        popularity_list.append(popularity)
        uri_list.append(uri)

    df = pd.DataFrame({
    'id' : id_list,
    'name' : name_list,
    'followers' : followers_list,
    'popularity' : popularity_list,
    'uri' : uri_list})

    return df

def sql_artist_to_dataframe(sql_artist):

    id_list = []
    name_list = []
    followers_list = []
    popularity_list = []
    uri_list = []

    id_list.append(sql_artist.id)
    name_list.append(sql_artist.name)
    followers_list.append(sql_artist.followers)
    popularity_list.append(sql_artist.popularity)
    uri_list.append(sql_artist.uri)

    df = pd.DataFrame({
    'id' : id_list,
    'name' : name_list,
    'followers' : followers_list,
    'popularity' : popularity_list,
    'uri' : uri_list})

    return df

def top10_tracks_to_dataframe(artist_list):

    global country

    track_list = pd.DataFrame()

    for query in artist_list:

        uri = search_artist(query)
        top10_tracks = get_top10_tracks(uri, country)

        id_list = []
        name_list = []
        popularity_list = []
        duration_list = []
        artists_list = []
        country_list = []
        artist_id_list = []
        release_date_list = []
        album_list = []
        uri_list = []

        for i in range(len(top10_tracks['tracks'])):

            id = top10_tracks['tracks'][i]['id']
            name = top10_tracks['tracks'][i]['name']
            popularity = int(top10_tracks['tracks'][i]['popularity'])
            duration = int(top10_tracks['tracks'][i]['duration_ms'])
            duration = ms_to_duration(duration)
            artist = top10_tracks['tracks'][i]['artists'][0]['name']
            artist_id = top10_tracks['tracks'][i]['artists'][0]['id']
            release_date = top10_tracks['tracks'][i]['album']['release_date']
            album = top10_tracks['tracks'][i]['album']['name']
            uri = top10_tracks['tracks'][i]['uri']

            id_list.append(id)
            name_list.append(name)
            popularity_list.append(popularity)
            duration_list.append(duration)
            artists_list.append(artist)
            country_list.append(country)
            artist_id_list.append(artist_id)
            release_date_list.append(release_date)
            album_list.append(album)
            uri_list.append(uri)

        df_tracks = pd.DataFrame({
        'id' : id_list,
        'name' : name_list,
        'popularity' : popularity_list,
        'duration' : duration_list,
        'artist' : artists_list,
        'country' : country_list,
        'artist_id' : artist_id_list,
        'release_date' : release_date_list,
        'album' : album_list,
        'uri' : uri_list})

        track_list = pd.concat([track_list, df_tracks], ignore_index=True)

    setlist = track_list.sort_values(by='popularity', ascending=False, ignore_index=True)

    return setlist

def sql_top10_tracks_to_dataframe(sql_tracks):

    track_list = pd.DataFrame()

    id_list = []
    name_list = []
    popularity_list = []
    duration_list = []
    artist_list = []
    release_date_list = []
    album_list = []
    uri_list = []

    for i in range(len(sql_tracks)):

        id = sql_tracks[i].id
        name = sql_tracks[i].name
        popularity = int(sql_tracks[i].popularity)
        duration = int(sql_tracks[i].duration)
        duration = ms_to_duration(duration)
        artist = sql_tracks[i].artist
        release_date = sql_tracks[i].release_date
        album = sql_tracks[i].album
        uri = sql_tracks[i].uri

        id_list.append(id)
        name_list.append(name)
        popularity_list.append(popularity)
        duration_list.append(duration)
        artist_list.append(artist)
        release_date_list.append(release_date)
        album_list.append(album)
        uri_list.append(uri)

    df_tracks = pd.DataFrame({
    'id' : id_list,
    'name' : name_list,
    'popularity' : popularity_list,
    'duration' : duration_list,
    'artist' : artist_list,
    'release_date' : release_date_list,
    'album' : album_list,
    'uri' : uri_list})

    track_list = pd.concat([track_list, df_tracks], ignore_index=True)

    setlist = track_list.sort_values(by='popularity', ascending=False, ignore_index=True)

    return setlist


""" 
def get_total_setlist(artist_list, country):
    
    track_list = pd.DataFrame()

    for artist in artist_list:
        uri = search_artist(artist)
        top10_tracks = get_top10_tracks(uri, country)
        df_tracks = top10_tracks_to_dataframe(top10_tracks, country)
        track_list = pd.concat([track_list, df_tracks], ignore_index=True)

    setlist = track_list.sort_values(by='popularity', ascending=False, ignore_index=True)

    return setlist
 """
def calculate_setlist(setlist, setlist_duration):

    global total_setlist_duration
    temp_total_setlist_duration = str_to_timedelta('00:00:00')
    df_index = 0

    for i in range(len(setlist)):
        if temp_total_setlist_duration + str_to_timedelta(setlist['duration'].loc[setlist.index[i]]) < setlist_duration:
            temp_total_setlist_duration += str_to_timedelta(setlist['duration'].loc[setlist.index[i]])
            df_index = df_index + 1
            total_setlist_duration = temp_total_setlist_duration                
    return df_index

def calculate_total_duration(setlist, setlist_duration):
    
    global total_setlist_duration

    for i in range(len(setlist)):
        if total_setlist_duration + str_to_timedelta(setlist['duration'].loc[setlist.index[i]]) > setlist_duration:
            return str(total_setlist_duration)
        total_setlist_duration += str_to_timedelta(setlist['duration'].loc[setlist.index[i]])
    return total_setlist_duration

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

setlist_duration = str_to_timedelta('02:00:00')
total_setlist_duration = str_to_timedelta('00:00:00')

if __name__ == '__main__':

    #total_setlist = get_total_setlist(artist_list, country)
    
    #
    #print(final_setlist.to_string())
    #total_setlist.to_csv('setlist.csv')
    #final_setlist.to_csv('final_setlist.csv')
    
    #artists = artists_to_dataframe(artist_list)
    #artists.to_csv('artists.csv')

    """ total_setlist = pd.read_csv('setlist.csv')
    artists = pd.read_csv('artists.csv')
    df_index = calculate_setlist(total_setlist, setlist_duration)
    final_setlist = total_setlist.head(df_index + 1)    
    
    print(total_setlist.artist.unique().tolist()) """

    #print(artists['name'].tolist())
    #print(artists['followers'].tolist())
    #print((final_setlist).to_string())
    #print(df_index)
    #print(total_setlist)

    #print((final_setlist.artist == 'System Of A Down').sum())
    #print((final_setlist.artist == 'TOOL').sum())

    uri = 'spotify:artist:2aaLAng2L2aWD2FClzwiep'
    #artist = get_artist_stats(uri)
    tracks = get_top10_tracks(uri, country)
    print(tracks)



    """ df_index = calculate_setlist(total_setlist, setlist_duration)
    total_duration = calculate_total_duration(total_setlist, setlist_duration)

    print(df_index)
    print(total_duration) """
        




