# spotifyrecs
This project helps a user discover new music based on their tastes, and selects songs which are less likely to be recommended by the default Spotify algorithm.

After all the songs on a playlist are finished, Spotify will continue to play music that the user might like. However, these recommendations often feature the same music and popular artists, even when a user skips the songs or switches to a different album. 

spotifyrecs finds a user's top artists in the short-term past. It finds a related artist and an album by that artist randomly, to reduce the chance of repeated recommendations. Then, it creates popularity thresholds for that album, ensuring it doesn't pick a song that is very unpopular or very popular. spotifyrecs eliminates the chance that extremely well-known songs are the only ones suggested; it also increases randomness to allow for greater variety.
