import os

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()

SCOPE = "playlist-read-private playlist-read-collaborative"
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
SPOTIFY_USER_CACHE = ".spotify_user_cache"


def main():
    auth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=SPOTIFY_USER_CACHE,
        open_browser=False,
    )

    auth_url = auth.get_authorize_url()
    print("Spotify yetkilendirme linki:")
    print(auth_url)
    print()
    print("1. Bu linki tarayıcıda aç.")
    print("2. Spotify izin ekranını onayla.")
    print("3. Tarayıcının yönlendiği tam URL'yi buraya yapıştır.")
    redirected_url = input("Yönlenen URL: ").strip()

    code = auth.parse_response_code(redirected_url)
    if not code:
        raise SystemExit("Yetkilendirme kodu okunamadı.")

    auth.get_access_token(code, as_dict=True)
    print(f"{SPOTIFY_USER_CACHE} güncellendi. Spotify playlist okuma için kullanıcı token'ı hazır.")


if __name__ == "__main__":
    main()
