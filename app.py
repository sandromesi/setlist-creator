from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import spotify
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
downloads_path = str(Path.home() / "Downloads")

app = Flask(__name__)

ENV = 'prod'
    
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DEV_DATABASE_URI')
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xxpuwiqfvkqyzd:da7fcc9fcb3566197e050b2018441a04f91cb1efc46fa957a871b22d475c34ad@ec2-34-242-84-130.eu-west-1.compute.amazonaws.com:5432/d9tdl1vt568tmt'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

genres = db.Table('genres',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
)

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    uri = db.Column(db.String(200), unique=True, nullable=False)
    #tracks = db.relationship('Track', backref='artist', lazy=True)
    """ genres = db.relationship('Genre', secondary=genres, lazy='subquery',
        backref=db.backref('artists', lazy=True)) """
    genres = db.relationship('Genre', secondary=genres, backref='genres')

    def __init__(self, name, followers, popularity, uri):
        self.name = name
        self.followers = followers
        self.popularity = popularity
        self.uri = uri

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(200))
    release_date = db.Column(db.String(200))
    album = db.Column(db.String(200))
    uri = db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self, name, popularity, duration, artist, release_date, album, uri):
        self.name = name
        self.popularity = popularity
        self.duration = duration
        self.artist = artist
        self.release_date = release_date
        self.album = album
        self.uri = uri

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/submit', methods=['POST'])
def submit():

    if request.method == 'POST':
        query = request.form['artists-query']
        setlist_duration = request.form['setlist-duration']
        setlist_duration = spotify.str_to_timedelta(setlist_duration)
        artist_list = spotify.string_to_list(query)

        for artist in artist_list:
            if db.session.query(Artist).filter(func.lower(Artist.name) == func.lower(artist)).count() == 0:
                uri = spotify.search_artist(artist)
                artist_stats = spotify.get_artist_stats(uri)
                name = artist_stats['name']
                followers = int(artist_stats['followers']['total'])
                popularity = int(artist_stats['popularity'])
                uri = artist_stats['uri']           
                #for loop pra pegar os genres. (Ja programado em spotify.py)
                #artist_stats.genres.append(Genre object)

                data = Artist(name, followers, popularity, uri)
                db.session.add(data)

                top10_tracks = spotify.get_top10_tracks(uri, 'IE')
                for i in range(len(top10_tracks['tracks'])):
                    name = top10_tracks['tracks'][i]['name']
                    popularity = int(top10_tracks['tracks'][i]['popularity'])
                    duration = int(top10_tracks['tracks'][i]['duration_ms'])
                    artist = data.name
                    release_date = top10_tracks['tracks'][i]['album']['release_date']
                    album = top10_tracks['tracks'][i]['album']['name']
                    uri = top10_tracks['tracks'][i]['uri']
                    track_data = Track(name, popularity, duration, artist, release_date, album, uri)
                    db.session.add(track_data)

                db.session.commit()

            artists_dataframe = pd.DataFrame()
            total_setlist = pd.DataFrame()

        for artist in artist_list:
            sql_artist = db.session.query(Artist).filter(func.lower(Artist.name) == func.lower(artist)).first()
            artist_df = spotify.sql_artist_to_dataframe(sql_artist)
            artists_dataframe = pd.concat([artists_dataframe, artist_df], ignore_index=True)
            sql_tracks = db.session.query(Track).filter(func.lower(Track.artist) == func.lower(artist)).all()           
            tracks_df = spotify.sql_top10_tracks_to_dataframe(sql_tracks)
            total_setlist = pd.concat([total_setlist, tracks_df], ignore_index=True)

        #artists_dataframe = spotify.artists_to_dataframe(artist_list)
        #total_setlist = spotify.top10_tracks_to_dataframe(artist_list)

        total_setlist = total_setlist.sort_values(by='popularity', ascending=False, ignore_index=True)

        df_index = spotify.calculate_setlist(total_setlist, setlist_duration)
        total_duration = spotify.calculate_total_duration(total_setlist, setlist_duration)
        setlist = total_setlist.head(df_index + 1) 
        setlist_artists = setlist.artist.unique().tolist()
        setlist_artists_tracks_count = []

        artists_dataframe.to_csv(path_or_buf=downloads_path + '/artists_stats.csv')
        total_setlist.to_csv(path_or_buf=downloads_path + '/total_track_list.csv')
        setlist.to_csv(path_or_buf=downloads_path + '/setlist.csv')

        for artist in setlist_artists:
            setlist_artists_tracks_count.append(int((setlist.artist == artist).sum()))

        names = artists_dataframe['name'].tolist()
        followers = artists_dataframe['followers'].tolist()
        
        if query == '' or setlist_duration == '':
            return render_template('index.html', message='Please, artist name is required')
        return render_template('dashboard.html', 
        duration=total_duration,
        artists_tracks=setlist_artists,
        tracks_count=setlist_artists_tracks_count,
        names=names,
        followers=followers
        )

if __name__ == '__main__':
    app.run()