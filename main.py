import requests
from bs4 import BeautifulSoup
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#Environment variables to hide sensitive data.
CLIENT_ID = os.environ["ClientID"]
CLIENT_SECRET = os.environ["ClientSecret"]

#Web scrape top tracks from an inputted date.
date = input("Which year would you want to travel to? Type the date in this format YYYY-MM-DD: ")
billboard_charts_url = "https://www.billboard.com/charts/hot-100/"

#Shorten date to "year" for later purposes.
year = date.split("-")[0]

response = requests.get(url=billboard_charts_url + date)
top_one_hundred = response.text

#Use beautiful soup to parse data.
soup = BeautifulSoup(top_one_hundred, "html.parser")

song_titles = soup.select("h3.c-title.a-no-trucate")
song_list = [item.get_text().strip() for item in song_titles]

artist_names = soup.select("span.c-label.a-no-trucate")
artist_list = [item.get_text().strip() for item in artist_names]

#Create a dictionary of song titles and their corresponding song artists.
song_and_artist_list = dict(zip(artist_list, song_list))

#Authenticate Spotify and get user ID.
#Here is a video on how to set up authentication with Spotipy and the Spotify API:
# https://www.youtube.com/watch?v=3RGm4jALukM
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri="http://example.com",
                                               scope="playlist-modify-private",
                                               cache_path="token.txt"))

user_id = sp.current_user()["id"]

#Search song URIs in Spotify using spotipy and put in a list. Catch errors for non-existent tracks.
spotify_song_uris = []
for key, value in song_and_artist_list.items():
    spotify_result = sp.search(q=f"artist {key} track: {value} year: {year}", type="track")
    try:
        song_uri = spotify_result["tracks"]["items"][0]["uri"]
        spotify_song_uris.append(song_uri)
    except IndexError:
        print(f"{value} doesn't exist in Spotify. Skipped.")

# Create playlist and get playlist ID.
playlist = sp.user_playlist_create(user=user_id, name=f"{year} Billboard 100", public=False,
                        description="Tracks Played During Typhoon Yolanda")
playlist_id = playlist["id"]

#Add items in the playlist.
sp.playlist_add_items(playlist_id=playlist_id, items=spotify_song_uris, position=None)



