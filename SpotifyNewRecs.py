import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from statistics import mean
from statistics import stdev

# This class needs your Spotify client ID and client secret, as well as your
# user's id. (Instructions can be found on the Spotify for Developers site.)
client_id = ""
client_secret = ""
scope = "playlist-modify-private"
user = ""
spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id, client_secret, "http://localhost:8080", scope=scope))

class Explore:
    '''Allows exploration of related songs, artists, and albums on Spotify.
    Allows for the creation of playlists using these features.
    ''' 

    def top_user_artists(self):
        '''Finds the user's top artists from the short-term past. Returns a
        list containing the URIs (unique Spotify IDs) of these artists. 
        ''' 
        # We have to create a new authentication with a scope that allows us
        # to read the user's top artists.
        spotify_user = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id, client_secret, "http://localhost:8080", 
                scope="user-top-read"))
        results = spotify_user.current_user_top_artists(
            time_range = "short_term")
        if (results == None):
            return
        
        # Each item in "results" represents an artist. "items"  is a list of
        # these items.
        items = results['items']
        artist_uri_list = []

        while (items):
            current = items.pop()
            artist_uri_list.append(current['uri'])

        return artist_uri_list

    def pick_random_element(self, element_list = []):
        '''Picks a random element from the input list and returns it. '''
        if (len(element_list) == 0):
            return
   
        input_list = element_list.copy()
        index = random.randint(0, len(input_list) - 1)
        return input_list.pop(index)

    def find_related_artists(self, artist_uri):
        '''Finds the artists related to a given artist. Takes the given
        artist's URI as input, and returns a list of related artist URIs.
        '''
        artist_info = spotify.artist_related_artists(artist_uri)['artists']
        artist_uri_list = []
        if (artist_info == None):
            return

        while (artist_info):
               artist_uri_list.append(artist_info.pop()['uri'])

        return artist_uri_list

    def find_albums(self, artist_uri):
        ''' Finds all the albums an artist has on Spotify. Takes the artist's
        URI as input and returns a list of album URIs.
        '''
        album_info = spotify.artist_albums(artist_uri)
        items = album_info['items']
        album_uri_list = []

        while (items):
            album_uri_list.append(items.pop()['uri'])
      
        if (len(album_uri_list) == 0):
            print("No related albums found!")
            return
        
        return album_uri_list

    def lower_threshold(self, album_uri):
        ''' Calculates the lower popularity threshold for a given album. This
        number is used by other functions to determine whether an album's song
        should be added to a playlist. The lower threshold is defined as 2
        standard deviations below the album's average song popularity.
        '''
        tracks = spotify.album(album_uri)['tracks']
        items = tracks['items']
        popularities = []
        if (tracks == None):
            return

        while (items):
            current = items.pop()
            popularities.append(spotify.track(current['id'])['popularity'])

        if (len(popularities) == 1):
            # If there's only one song on the album, the minimum threshold is
            # just the song's popularity.
            return popularities.pop()

        threshold = int(mean(popularities) - 2*stdev(popularities))
        if (threshold >= 0):
            return threshold
        else:
            return 0 # If the threshold is negative, make it zero

    def pick_song(self, album_uri, max_popularity = 60):
        ''' Picks a song from an album. Takes an album_uri as input, and an
        optional max popularity threshold. Returns the URI of a random song 
        whose popularity is between max_popularity (inclusive) and the 
        album's lower popularity threshold (inclusive, defined by the function
        lower_threshold).
        '''
        tracks = spotify.album(album_uri)['tracks']
        items = tracks['items']
        song_options = []
        lower_threshold = self.lower_threshold(album_uri)
        if (tracks == None):
            return

        while (items):
            current = items.pop()
            popularity = spotify.track(current['id'])['popularity']
            
            if ((popularity >= lower_threshold) and 
                (popularity <= max_popularity)):
                song_options.append(current['id'])

        return self.pick_random_element(song_options)

    def name_playlist(self, artist_uri):
        ''' Creates a playlist name based on an input artist. Name is in the
        format "songs like [artist name], [month].[day].[year]".
        '''
        now = datetime.now()
        artist_name = spotify.artist(artist_uri)['name']
        return "songs like " + artist_name + ", {0}.{1}.{2}".format(now.month,
                                                                    now.day, 
                                                                    now.year)
        
    def create_playlist(self, max_popularity = 60):
        '''Using one of the user's top artists, creates a playlist of up to 10
        recommended songs. Songs are recommended by repeatedly: picking a 
        random related artist, picking a random album from that related
        artist, and picking a song in that album within popularity thresholds.
        '''
        songs = []

        # Pick a random artist that the user likes. Then, name the playlist.
        top_artist = self.pick_random_element(self.top_user_artists())
        playlist_name = self.name_playlist(top_artist)

        # Create the (private) playlist, and store its uri.
        playlist_uri = spotify.user_playlist_create(
            user, playlist_name, public = False, description="auto-created")['uri']    
        song_index = 0
        artist_index = 0

        while (song_index < 10):
            # Generate a list of artists related to the top artist, and pick
            # a random one.
            related_artist = self.pick_random_element(
                                  self.find_related_artists(top_artist))

            # This inner loop allows us to add up to 2 songs by the same 
            # related artist before the variable related_artist is reset.
            while (artist_index < 2):
                # Generate a list of albums by the related artist, and pick a 
                # random one.
                album = self.pick_random_element(self.find_albums(related_artist))

                # Pick a song from this album that's below the max threshold.
                current_song = self.pick_song(album, max_popularity)

                if ((current_song is not None) and (current_song not in songs)):
                    songs.append(current_song)
                    
                artist_index += 1

            song_index += 2
            # Reset the artist index, since a new artist will be picked.
            artist_index = 0

        # Add the songs to the playlist.
        spotify.user_playlist_add_tracks(user, playlist_uri, songs)
        return


def main():
    e = Explore()
    e.create_playlist()
    return

if __name__ == "__main__":
    main()
