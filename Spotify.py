import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="bdfa9905e54446b5aeb083d0d45b3d52",
    client_secret="eeab546554f74c37b7878e2bc358e26b",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-modify-playback-state user-read-playback-state"
))


cancion = input("Ingrese el nombre de la canción que desea buscar: ")

resultados = sp.search(q=cancion, type='track', limit=1)

if len(resultados['tracks']['items']) == 0:
    print("deje de inventar canciones")
else:
    track = resultados['tracks']['items'][0]
    track_uri = track['uri']
    nombre = track['name']
    artista = track['artists'][0]['name']
    
    print(f"Reproduciendo '{nombre}' de {artista}.")

dispositivos = sp.devices()
if len(dispositivos['devices']) == 0:
    print("Jajaja no tiene premium")
else:
    device_id = dispositivos['devices'][0]['id']
    sp.start_playback(device_id=device_id, uris=[track_uri])