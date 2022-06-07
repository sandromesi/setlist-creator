from importlib.resources import path
from flask import Flask, render_template, request
import spotify
import csv
from pathlib import Path
downloads_path = str(Path.home() / "Downloads")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():

    if request.method == 'POST':
        query = request.form['artist-query']
        uri = spotify.search_artist(query)
        artist = spotify.get_artist_stats(uri)
        top10_tracks = spotify.get_top10_tracks(uri)

        csv_name = spotify.create_csv_name(artist)
        spotify.create_artist_csv(artist, csv_name)
        spotify.create_top10_tracks_csv(top10_tracks, csv_name)
        
        if query == '':
            return render_template('index.html', message='Please, artist name is required')
        return render_template('success.html', filepath = downloads_path)



if __name__ == '__main__':
    app.debug = True
    app.run()