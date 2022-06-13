from flask import Flask, render_template, request
import spotify
from pathlib import Path
downloads_path = str(Path.home() / "Downloads")

app = Flask(__name__)

""" ENV = 'dev'
    
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgresandromesi:7_xJR"/eAxRnvRg.30u#!SQ[z<@localhost/gig_setlist_creator'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) """

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
        artists_dataframe = spotify.artists_to_dataframe(artist_list)
        total_setlist = spotify.top10_tracks_to_dataframe(artist_list)
        df_index = spotify.calculate_setlist(total_setlist, setlist_duration)
        total_duration = spotify.calculate_total_duration(total_setlist, setlist_duration)
        setlist = total_setlist.head(df_index + 1) 
        setlist_artists = setlist.artist.unique().tolist()
        setlist_artists_tracks_count = []

        artists_dataframe.to_csv(path_or_buf=downloads_path + '/artists_stats.csv')
        total_setlist.to_csv(path_or_buf=downloads_path + '/total_track_list.csv')
        setlist.to_csv(path_or_buf=downloads_path + '/setlist.csv')

        print('--------------------------------------------')
        print(downloads_path + '/total_track_list.csv')
        print('--------------------------------------------')

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