import discord
from discord import app_commands
from discord.ext import tasks, commands
import wavelink
import yt_dlp
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import asyncio
import os
import random
import re
import socket
import time
import json
import difflib
import lyricsgenius
import aiohttp
import requests
import datetime
from datetime import date
import pytz
from dotenv import load_dotenv
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

_ORIGINAL_GETADDRINFO = socket.getaddrinfo
_DISCORD_DNS_SUFFIXES = ("discord.com", "discord.gg", "discordapp.com", "discord.media")

def _install_discord_dns_override():
    try:
        import dns.resolver
    except ImportError:
        return

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
    resolver.timeout = 3
    resolver.lifetime = 5

    def getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        hostname = str(host).rstrip(".").lower()
        if hostname.endswith(_DISCORD_DNS_SUFFIXES):
            try:
                addresses = [str(answer) for answer in resolver.resolve(hostname, "A")]
                results = []
                for address in addresses:
                    results.extend(_ORIGINAL_GETADDRINFO(address, port, family, type, proto, flags))
                if results:
                    return results
            except Exception as exc:
                print(f"Discord DNS override failed for {hostname}: {exc}")
        return _ORIGINAL_GETADDRINFO(host, port, family, type, proto, flags)

    socket.getaddrinfo = getaddrinfo

_install_discord_dns_override()

# ── Tokenlar & Ayarlar ────────────────────────────────────────────────────────
DISCORD_TOKEN  = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_TOKEN   = os.getenv("GENIUS_TOKEN")
EXA_API_KEY    = os.getenv("EXA_API_KEY")
APIF_KEY       = os.getenv("APIF_KEY")
FD_KEY         = os.getenv("FD_KEY")

HABER_KANAL_ID   = 1500441325047386152
FUTBOL_KANAL_ID  = 1490431891545784471
WIKI_KANAL_ID    = 1492870597988847626
HABER_SAATI      = datetime.time(hour=15, minute=0)   # UTC 15:00 = TR 18:00
WIKI_SAATI       = datetime.time(hour=9, minute=0)    # UTC 09:00 = TR 12:00
WIKI_OLAY_SAYISI = 5
TURKEY_TZ        = pytz.timezone("Europe/Istanbul")

APIF_HOST = "v3.football.api-sports.io"
APIF_URL  = f"https://{APIF_HOST}"
FD_URL    = "https://api.football-data.org/v4"

# ── Spotify & Genius ──────────────────────────────────────────────────────────
SPOTIFY_CLIENT_CACHE = ".spotify_client_cache"
SPOTIFY_USER_CACHE = ".spotify_user_cache"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT,
    client_secret=SPOTIFY_SECRET,
    cache_handler=CacheFileHandler(cache_path=SPOTIFY_CLIENT_CACHE),
))
genius = lyricsgenius.Genius(GENIUS_TOKEN, timeout=10, retries=2)

FFMPEG_OPTS = {
    "before_options": "-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_on_network_error 1 -reconnect_on_http_error 4xx,5xx -reconnect_delay_max 7",
    "options": "-vn",
}
executor = ThreadPoolExecutor(max_workers=4)
METADATA_CACHE_FILE = "music_metadata_cache.json"
MUSIC_PLAYLISTS_FILE = "music_playlists.json"
METADATA_CACHE_TTL = 60 * 60 * 24 * 7
PROGRESS_BAR_LENGTH = 18
LAVALINK_HOST = os.getenv("LAVALINK_HOST")
LAVALINK_PORT = os.getenv("LAVALINK_PORT")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")
LAVALINK_URI = os.getenv("LAVALINK_URI") or (
    f"http://{LAVALINK_HOST}:{LAVALINK_PORT}" if LAVALINK_HOST and LAVALINK_PORT else None
)

# ── Futbol Sabitleri ──────────────────────────────────────────────────────────
FD_LEAGUES = {
    "premier":    {"code": "PL",  "name": "Premier League",   "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    "laliga":     {"code": "PD",  "name": "La Liga",          "emoji": "🇪🇸"},
    "bundesliga": {"code": "BL1", "name": "Bundesliga",       "emoji": "🇩🇪"},
    "seriea":     {"code": "SA",  "name": "Serie A",          "emoji": "🇮🇹"},
    "ligue1":     {"code": "FL1", "name": "Ligue 1",          "emoji": "🇫🇷"},
    "ucl":        {"code": "CL",  "name": "Sampiyonlar Ligi", "emoji": "⭐"},
}
APIF_ALL_IDS = {39, 140, 78, 135, 61, 2, 3, 848, 203}
LEAGUE_EMOJIS = {
    39: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", 140: "🇪🇸", 78: "🇩🇪", 135: "🇮🇹",
    61: "🇫🇷", 2: "⭐", 3: "🟠", 848: "🔵", 203: "🇹🇷"
}
LIVE_STATUSES_APIF = {"1H", "HT", "2H", "ET", "BT", "P", "LIVE"}
STAGE_NAMES = {
    "PLAYOFFS":       "🎯 Play-off",
    "LAST_16":        "🔟 Son 16",
    "ROUND_OF_16":    "🔟 Son 16",
    "QUARTER_FINALS": "⚽ Çeyrek Final",
    "SEMI_FINALS":    "🔥 Yarı Final",
    "FINAL":          "🏆 Final",
}

# ── Bot ───────────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.voice_states = True

class HoslafBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        self.loop.create_task(connect_lavalink())
        gunluk_haber.start()
        daily_schedule_task.start()
        gunluk_wiki.start()
        if not music_progress_task.is_running():
            music_progress_task.start()
        print("Slash komutları senkronize edildi.")

bot = HoslafBot()

@dataclass
class Track:
    source: str
    query: str
    title: str | None = None
    webpage_url: str | None = None
    thumbnail: str | None = None
    duration: int | None = None
    uploader: str | None = None
    audio_url: str | None = None
    requester_id: int | None = None
    requester_name: str | None = None
    resolved: bool = False
    attempts: int = 0
    resume_at: int = 0

    @classmethod
    def search(cls, query: str, requester_id: int | None = None, requester_name: str | None = None):
        return cls(source="search", query=query, title=query, requester_id=requester_id, requester_name=requester_name)

    @classmethod
    def url(cls, url: str, title: str | None = None, requester_id: int | None = None, requester_name: str | None = None):
        return cls(source="url", query=url, title=title or "Link", webpage_url=url, requester_id=requester_id, requester_name=requester_name)

    @classmethod
    def from_metadata(cls, query: str, metadata: dict, requester_id: int | None = None, requester_name: str | None = None):
        return cls(
            source="resolved",
            query=query,
            title=metadata.get("title") or query,
            webpage_url=metadata.get("webpage_url"),
            thumbnail=metadata.get("thumbnail"),
            duration=metadata.get("duration"),
            uploader=metadata.get("uploader"),
            audio_url=metadata.get("audio_url"),
            requester_id=requester_id,
            requester_name=requester_name,
            resolved=True,
            resume_at=metadata.get("resume_at", 0) or 0,
        )

    @property
    def display_title(self):
        return self.title or self.query

    def resolve_query(self):
        if self.source == "search":
            return f"ytsearch:{self.query}"
        return self.webpage_url or self.query

    def update_from_metadata(self, metadata: dict):
        self.title = metadata.get("title") or self.title or self.query
        self.webpage_url = metadata.get("webpage_url") or self.webpage_url
        self.thumbnail = metadata.get("thumbnail") or self.thumbnail
        self.duration = metadata.get("duration") or self.duration
        self.uploader = metadata.get("uploader") or self.uploader
        self.audio_url = metadata.get("audio_url")
        self.resolved = True

    def metadata(self):
        return {
            "audio_url": self.audio_url,
            "title": self.display_title,
            "webpage_url": self.webpage_url,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
            "uploader": self.uploader,
            "resume_at": self.resume_at,
        }

    def cache_key(self):
        return normalize_track_title(self.webpage_url or self.query)

@dataclass
class MusicPlayer:
    guild_id: int
    queue: list[Track] = field(default_factory=list)
    current: Track | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    prefetch_task: asyncio.Task | None = None
    text_channel_id: int | None = None
    voice_channel_id: int | None = None
    volume: float = 0.8
    mode: str = "music"
    starting: bool = False
    skip_requested: bool = False
    manual_disconnect: bool = False
    ignore_next_after: bool = False
    autoplay: bool = False
    repeat_mode: str = "off"
    history: list[Track] = field(default_factory=list)
    panel_message_id: int | None = None
    playback_generation: int = 0
    idle_task: asyncio.Task | None = None
    current_started_at: float | None = None
    current_elapsed_offset: int = 0
    paused_at: float | None = None

players: dict[int, MusicPlayer] = {}
MUSIC_STATS_FILE = "music_stats.json"
LAVALINK_CONNECTED = False

def get_player(guild_id: int) -> MusicPlayer:
    player = players.get(guild_id)
    if player is None:
        player = MusicPlayer(guild_id=guild_id)
        players[guild_id] = player
    return player

async def connect_lavalink():
    global LAVALINK_CONNECTED
    await bot.wait_until_ready()
    if not LAVALINK_URI or not LAVALINK_PASSWORD:
        print("Lavalink ayarlari eksik. LAVALINK_URI veya LAVALINK_HOST/PORT ve LAVALINK_PASSWORD gerekli.")
        return
    for attempt in range(1, 6):
        try:
            if wavelink.Pool.nodes:
                LAVALINK_CONNECTED = True
                return
            node = wavelink.Node(identifier="hoslaf-main", uri=LAVALINK_URI, password=LAVALINK_PASSWORD)
            await wavelink.Pool.connect(nodes=[node], client=bot, cache_capacity=256)
            LAVALINK_CONNECTED = True
            print(f"Lavalink baglandi: {LAVALINK_URI}")
            return
        except Exception as exc:
            LAVALINK_CONNECTED = False
            print(f"Lavalink baglanti denemesi {attempt}/5 basarisiz: {exc}")
            await asyncio.sleep(5 * attempt)

async def ensure_lavalink_ready():
    if wavelink.Pool.nodes:
        return
    await connect_lavalink()
    if not wavelink.Pool.nodes:
        raise RuntimeError("Lavalink baglantisi hazir degil.")

def is_lavalink_player(vc):
    return isinstance(vc, wavelink.Player)

def voice_is_playing(vc):
    if not vc:
        return False
    if is_lavalink_player(vc):
        return bool(vc.playing)
    return vc.is_playing()

def voice_is_paused(vc):
    if not vc:
        return False
    if is_lavalink_player(vc):
        return bool(vc.paused)
    return vc.is_paused()

async def voice_stop(vc):
    if not vc:
        return
    if is_lavalink_player(vc):
        await vc.stop()
    else:
        vc.stop()

async def voice_pause(vc, paused: bool):
    if not vc:
        return
    if is_lavalink_player(vc):
        await vc.pause(paused)
    elif paused:
        vc.pause()
    else:
        vc.resume()

async def voice_set_volume(vc, volume: float):
    if not vc:
        return
    if is_lavalink_player(vc):
        await vc.set_volume(max(0, min(150, int(volume * 100))))
    elif vc.source and hasattr(vc.source, "volume"):
        vc.source.volume = volume

async def ensure_voice_player(guild, voice_channel):
    await ensure_lavalink_ready()
    vc = guild.voice_client
    if vc is None:
        return await voice_channel.connect(cls=wavelink.Player, self_deaf=True)
    if not is_lavalink_player(vc):
        await vc.disconnect(force=True)
        return await voice_channel.connect(cls=wavelink.Player, self_deaf=True)
    if vc.channel != voice_channel:
        await vc.move_to(voice_channel)
    return vc

def load_music_stats():
    try:
        with open(MUSIC_STATS_FILE, "r", encoding="utf-8") as stats_file:
            return json.load(stats_file)
    except (FileNotFoundError, ValueError):
        return {"users": {}}

def save_music_stats(stats):
    with open(MUSIC_STATS_FILE, "w", encoding="utf-8") as stats_file:
        json.dump(stats, stats_file, ensure_ascii=False, indent=2)

def load_json_file(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as data_file:
            data = json.load(data_file)
            return data if isinstance(data, type(fallback)) else fallback
    except (FileNotFoundError, ValueError):
        return fallback

def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as data_file:
        json.dump(data, data_file, ensure_ascii=False, indent=2)

def get_cached_metadata(key: str):
    cache = load_json_file(METADATA_CACHE_FILE, {})
    item = cache.get(key)
    if not item:
        return None
    if time.time() - float(item.get("cached_at", 0)) > METADATA_CACHE_TTL:
        cache.pop(key, None)
        save_json_file(METADATA_CACHE_FILE, cache)
        return None
    metadata = item.get("metadata")
    return metadata if isinstance(metadata, dict) else None

def set_cached_metadata(key: str, metadata: dict):
    if not key or not metadata:
        return
    cache = load_json_file(METADATA_CACHE_FILE, {})
    cache[key] = {"cached_at": time.time(), "metadata": metadata}
    if len(cache) > 600:
        for old_key, _ in sorted(cache.items(), key=lambda item: item[1].get("cached_at", 0))[:100]:
            cache.pop(old_key, None)
    save_json_file(METADATA_CACHE_FILE, cache)

def load_music_playlists():
    return load_json_file(MUSIC_PLAYLISTS_FILE, {})

def save_music_playlists(playlists):
    save_json_file(MUSIC_PLAYLISTS_FILE, playlists)

def serialize_track(track: Track):
    return {
        "source": track.source,
        "query": track.query,
        "title": track.title,
        "webpage_url": track.webpage_url,
        "thumbnail": track.thumbnail,
        "duration": track.duration,
        "uploader": track.uploader,
    }

def deserialize_track(data: dict, requester_id: int | None = None, requester_name: str | None = None):
    return Track(
        source=data.get("source") or "search",
        query=data.get("query") or data.get("webpage_url") or data.get("title") or "Bilinmeyen sarki",
        title=data.get("title"),
        webpage_url=data.get("webpage_url"),
        thumbnail=data.get("thumbnail"),
        duration=data.get("duration"),
        uploader=data.get("uploader"),
        requester_id=requester_id,
        requester_name=requester_name,
    )

def record_music_stat(guild_id: int, track: Track):
    if not track.requester_id:
        return
    stats = load_music_stats()
    key = f"{guild_id}:{track.requester_id}"
    user = stats.setdefault("users", {}).setdefault(
        key,
        {"name": track.requester_name or str(track.requester_id), "tracks": 0, "duration": 0, "top_tracks": {}, "top_artists": {}},
    )
    user["name"] = track.requester_name or user.get("name") or str(track.requester_id)
    user["tracks"] = int(user.get("tracks", 0)) + 1
    user["duration"] = int(user.get("duration", 0)) + int(track.duration or 0)
    top_tracks = user.setdefault("top_tracks", {})
    top_tracks[track.display_title] = int(top_tracks.get(track.display_title, 0)) + 1
    if track.uploader:
        top_artists = user.setdefault("top_artists", {})
        top_artists[track.uploader] = int(top_artists.get(track.uploader, 0)) + 1
    save_music_stats(stats)

# ─────────────────────────────────────────────────────────────────────────────
#  MÜZİK YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────

def get_queue(guild_id):
    return get_player(guild_id).queue

def get_current_title(guild_id):
    current = get_player(guild_id).current
    return current.display_title if current else None

def is_playback_active(player: MusicPlayer, vc):
    return bool(
        player.starting
        or player.current
        or player.queue
        or (vc and (voice_is_playing(vc) or voice_is_paused(vc)))
    )

def is_spotify_url(t): return "spotify.com" in t or t.startswith("spotify:")
def is_url(t): return t.startswith("http://") or t.startswith("https://")
def is_spotify_playlist_url(t): return ("spotify.com/playlist" in t) or t.startswith("spotify:playlist:")
def is_spotify_album_url(t): return ("spotify.com/album" in t) or t.startswith("spotify:album:")
def is_playlist_url(t): return ("list=" in t) or is_spotify_playlist_url(t) or is_spotify_album_url(t)

class SpotifyPlaylistError(Exception):
    pass

def friendly_music_error(error):
    message = str(error)
    lowered = message.lower()
    if isinstance(error, SpotifyPlaylistError) or "spotify" in lowered:
        return "Spotify bağlantısını okuyamadım. Playlist için Spotify yetkilendirmesi gerekebilir."
    if "extractor" in lowered or "video unavailable" in lowered or "requested format" in lowered:
        return "Bu şarkıyı bulamadım veya oynatılabilir format alamadım. Farklı bir isim ya da link deneyebilirsin."
    if "timed out" in lowered or "timeout" in lowered or "10054" in lowered:
        return "Müzik kaynağına bağlanırken ağ kesintisi oldu. Birazdan tekrar deneyebilirsin."
    return "Müzik işlemi tamamlanamadı. Farklı bir isim ya da link deneyebilirsin."

def _spotify_id(url, kind):
    patterns = [
        rf"open\.spotify\.com/(?:intl-[a-z]{{2}}/)?{kind}/([A-Za-z0-9]+)",
        rf"spotify:{kind}:([A-Za-z0-9]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise SpotifyPlaylistError(f"Spotify {kind} linki okunamadı.")

def _spotify_user_token():
    try:
        import json
        with open(SPOTIFY_USER_CACHE, "r", encoding="utf-8") as cache_file:
            token_info = json.load(cache_file)
    except (FileNotFoundError, ValueError):
        return None
    if token_info.get("expires_at", 0) > time.time() + 60:
        return token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")
    if not refresh_token:
        return None
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT,
        client_secret=SPOTIFY_SECRET,
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
        scope="playlist-read-private playlist-read-collaborative",
        cache_path=SPOTIFY_USER_CACHE,
        open_browser=False,
    )
    refreshed = auth_manager.refresh_access_token(refresh_token)
    return refreshed.get("access_token")

def _spotify_client_token():
    import requests
    token_resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT, SPOTIFY_SECRET),
        timeout=20,
    )
    if token_resp.status_code != 200:
        raise SpotifyPlaylistError(f"Spotify token alınamadı ({token_resp.status_code}).")
    token = token_resp.json().get("access_token")
    if not token:
        raise SpotifyPlaylistError("Spotify token yanıtı boş geldi.")
    return token

def _spotify_get_json(url, token, params=None):
    import requests
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=30,
    )
    if response.status_code in (401, 403):
        raise SpotifyPlaylistError(
            "Spotify playlist içeriği için kullanıcı yetkisi gerekiyor. "
            "Spotify'ın yeni API kurallarında bazı playlistler client id/secret ile açılamıyor."
        )
    if response.status_code != 200:
        raise SpotifyPlaylistError(f"Spotify API hata döndürdü ({response.status_code}).")
    return response.json()

def _spotify_track_to_query(track):
    if not track or track.get("type") not in (None, "track") or track.get("is_local"):
        return None
    name = track.get("name")
    artists = ", ".join(a.get("name", "") for a in track.get("artists", []) if a.get("name"))
    if not name or not artists:
        return None
    return f"{artists} - {name}"

def _spotify_to_search_query(url):
    track_id = _spotify_id(url, "track")
    track = sp.track(track_id)
    query = _spotify_track_to_query(track)
    if not query:
        raise SpotifyPlaylistError("Spotify şarkısı okunamadı.")
    return query

def _spotify_playlist_to_queries(url):
    queries = []
    if is_spotify_playlist_url(url):
        playlist_id = _spotify_id(url, "playlist")
        token = _spotify_user_token() or _spotify_client_token()
        offset = 0
        while True:
            try:
                data = _spotify_get_json(
                    f"https://api.spotify.com/v1/playlists/{playlist_id}/items",
                    token,
                    {"limit": 100, "offset": offset, "additional_types": "track"},
                )
            except SpotifyPlaylistError:
                data = _spotify_get_json(
                    f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                    _spotify_client_token(),
                    {"limit": 100, "offset": offset, "additional_types": "track"},
                )
            for item in data.get("items", []):
                query = _spotify_track_to_query(item.get("item") or item.get("track"))
                if query:
                    queries.append(query)
            if not data.get("next"):
                break
            offset += 100
    elif is_spotify_album_url(url):
        album_id = _spotify_id(url, "album")
        token = _spotify_client_token()
        offset = 0
        while True:
            data = _spotify_get_json(
                f"https://api.spotify.com/v1/albums/{album_id}/tracks",
                token,
                {"limit": 50, "offset": offset},
            )
            for track in data.get("items", []):
                query = _spotify_track_to_query(track)
                if query:
                    queries.append(query)
            if not data.get("next"):
                break
            offset += 50
    return queries

YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "nocheckcertificate": True,
    "no_warnings": True,
    "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
}

def _fetch_audio(query):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return {
            "audio_url": info["url"],
            "title": info.get("title", "Bilinmeyen Şarkı"),
            "webpage_url": info.get("webpage_url") or info.get("original_url"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader") or info.get("channel"),
        }

def _fetch_playlist_yt(url):
    opts = {**YDL_OPTS, "noplaylist": False, "extract_flat": True}
    tracks = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "entries" in info:
            for entry in info["entries"]:
                if entry and entry.get("id"):
                    tracks.append((f"https://www.youtube.com/watch?v={entry['id']}", entry.get("title", "Bilinmeyen Şarkı")))
    return tracks

def _fetch_search_results(query, limit=8):
    opts = {**YDL_OPTS, "extract_flat": True}
    results = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        for entry in info.get("entries", []):
            if not entry:
                continue
            video_id = entry.get("id")
            webpage_url = entry.get("webpage_url") or entry.get("url")
            if webpage_url and not webpage_url.startswith("http") and video_id:
                webpage_url = f"https://www.youtube.com/watch?v={video_id}"
            if not webpage_url and video_id:
                webpage_url = f"https://www.youtube.com/watch?v={video_id}"
            if webpage_url:
                results.append({
                    "url": webpage_url,
                    "title": entry.get("title") or query,
                    "duration": entry.get("duration"),
                    "thumbnail": entry.get("thumbnail"),
                    "uploader": entry.get("uploader") or entry.get("channel"),
                })
    return results

async def fetch_audio(query):
    return await asyncio.get_event_loop().run_in_executor(executor, _fetch_audio, query)

async def fetch_playlist_yt(url):
    return await asyncio.get_event_loop().run_in_executor(executor, _fetch_playlist_yt, url)

async def fetch_search_results(query, limit=8):
    return await asyncio.get_event_loop().run_in_executor(executor, _fetch_search_results, query, limit)

async def spotify_to_search_query(url):
    return await asyncio.get_event_loop().run_in_executor(executor, _spotify_to_search_query, url)

async def spotify_playlist_to_queries(url):
    return await asyncio.get_event_loop().run_in_executor(executor, _spotify_playlist_to_queries, url)

async def resolve_queue_item(item):
    if isinstance(item, Track):
        await resolve_track(item)
        return item
    if len(item) >= 3 and isinstance(item[2], dict):
        return Track.from_metadata(item[1], item[2])
    if item[0] == "__search__":
        track = Track.search(item[1])
        await resolve_track(track)
        return track
    if item[0] == "__url__":
        track = Track.url(item[1])
        await resolve_track(track)
        return track
    if isinstance(item[0], str) and item[0].startswith("https://www.youtube.com/watch"):
        track = Track.url(item[0], item[1])
        await resolve_track(track)
        return track
    return item

async def resolve_track(track: Track, *, refresh_audio: bool = False):
    if track.resolved and track.audio_url and not refresh_audio:
        return track
    cache_key = track.cache_key()
    if not refresh_audio:
        cached = get_cached_metadata(cache_key)
        if cached:
            track.update_from_metadata(cached)
            return track
    metadata = await fetch_audio(track.resolve_query())
    track.update_from_metadata(metadata)
    set_cached_metadata(cache_key, metadata)
    return track

async def resolve_lavalink_track(track: Track):
    await ensure_lavalink_ready()
    query = track.webpage_url or track.query
    source = None if is_url(query) else wavelink.TrackSource.YouTubeMusic
    results = await wavelink.Playable.search(query, source=source)
    if not results:
        raise RuntimeError("Lavalink sarkiyi bulamadi.")
    playable = results[0]
    track.title = getattr(playable, "title", None) or track.title or track.query
    track.webpage_url = getattr(playable, "uri", None) or track.webpage_url
    track.thumbnail = getattr(playable, "artwork", None) or track.thumbnail
    track.duration = int(getattr(playable, "length", 0) / 1000) if getattr(playable, "length", 0) else track.duration
    track.uploader = getattr(playable, "author", None) or track.uploader
    track.resolved = True
    track.audio_url = track.webpage_url
    playable.extras = {"hoslaf_query": track.query}
    return playable

async def prefetch_queue(guild_id):
    player = get_player(guild_id)
    queue = player.queue
    index = 0
    while index < len(queue):
        item = queue[index]
        if isinstance(item, Track) and item.resolved:
            index += 1
            continue
        try:
            resolved = await resolve_queue_item(item)
            if index < len(queue) and queue[index] == item:
                queue[index] = resolved
                index += 1
        except Exception as exc:
            print(f"Kuyruk on hazirlama hatasi: {exc}")
            index += 1

def schedule_queue_prefetch(guild_id):
    player = get_player(guild_id)
    if player.prefetch_task and not player.prefetch_task.done():
        return
    player.prefetch_task = bot.loop.create_task(prefetch_queue(guild_id))

def format_duration(seconds):
    if not seconds:
        return "Bilinmiyor"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

def current_position(player: MusicPlayer):
    if not player.current:
        return 0
    elapsed = int(player.current_elapsed_offset or 0)
    if player.paused_at:
        return elapsed
    if player.current_started_at:
        elapsed += max(0, int(time.monotonic() - player.current_started_at))
    if player.current.duration:
        return min(elapsed, int(player.current.duration))
    return elapsed

def build_progress_bar(player: MusicPlayer):
    current = player.current
    if not current:
        return "Beklemede"
    elapsed = current_position(player)
    duration = int(current.duration or 0)
    if duration <= 0:
        return f"{format_duration(elapsed)} ======o====== Bilinmiyor"
    ratio = max(0, min(1, elapsed / duration))
    cursor_index = min(PROGRESS_BAR_LENGTH - 1, int(ratio * PROGRESS_BAR_LENGTH))
    bar = "".join("o" if i == cursor_index else ("=" if i < cursor_index else "-") for i in range(PROGRESS_BAR_LENGTH))
    return f"{format_duration(elapsed)} {bar} {format_duration(duration)}"

def ffmpeg_options_for_seek(seconds: int = 0):
    if seconds and seconds > 0:
        return {
            "before_options": f"{FFMPEG_OPTS['before_options']} -ss {int(seconds)}",
            "options": FFMPEG_OPTS["options"],
        }
    return FFMPEG_OPTS

def total_queue_duration(player: MusicPlayer):
    known = sum(int(track.duration or 0) for track in player.queue)
    unknown = sum(1 for track in player.queue if not track.duration)
    if not known and unknown:
        return "Bilinmiyor"
    suffix = f" (+{unknown} bilinmeyen)" if unknown else ""
    return format_duration(known) + suffix

def queue_title(item):
    if isinstance(item, Track):
        return item.display_title
    if len(item) >= 3 and isinstance(item[2], dict):
        return item[2].get("title", item[1])
    return item[1]

def requester_label(track: Track):
    return track.requester_name or "Bilinmiyor"

def normalize_track_title(title):
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()

def is_similar_track(candidate: Track, previous: Track):
    if candidate.webpage_url and previous.webpage_url and candidate.webpage_url == previous.webpage_url:
        return True
    candidate_title = normalize_track_title(candidate.display_title)
    previous_title = normalize_track_title(previous.display_title)
    if not candidate_title or not previous_title:
        return False
    if candidate_title == previous_title:
        return True
    if candidate_title in previous_title or previous_title in candidate_title:
        return True
    return difflib.SequenceMatcher(None, candidate_title, previous_title).ratio() >= 0.88

async def pick_autoplay_track(player: MusicPlayer, seed_track: Track):
    seed_artist = seed_track.uploader or ""
    seed_title = seed_track.display_title
    search_queries = []
    if seed_artist:
        search_queries.extend([
            f"{seed_artist} mix",
            f"{seed_artist} popular songs",
            f"{seed_artist} playlist",
        ])
    search_queries.extend([
        f"{seed_title} radio",
        f"{seed_title} similar songs",
        f"{seed_title} mix",
    ])
    recent_tracks = player.history[-20:] + [seed_track]
    tried_titles = set()
    for query in search_queries:
        try:
            results = await fetch_search_results(query, limit=8)
        except Exception as exc:
            print(f"Otomatik oneri arama hatasi: {exc}")
            continue
        random.shuffle(results)
        for result in results:
            candidate = Track.url(
                result["url"],
                result.get("title"),
                requester_name="Otomatik Oneri",
            )
            candidate.duration = result.get("duration")
            candidate.thumbnail = result.get("thumbnail")
            candidate.uploader = result.get("uploader")
            title_key = normalize_track_title(candidate.display_title)
            if title_key in tried_titles:
                continue
            tried_titles.add(title_key)
            if any(is_similar_track(candidate, previous) for previous in recent_tracks):
                continue
            return candidate
    return None

def build_music_panel_embed(player: MusicPlayer):
    embed = discord.Embed(title="Muzik Paneli", color=0xDB2777)
    current = player.current
    if current:
        title = current.display_title
        url = current.webpage_url
        embed.description = f"**[{title}]({url})**" if url else f"**{title}**"
        embed.add_field(name="Ilerleme", value=build_progress_bar(player), inline=False)
        embed.add_field(name="Ses", value=f"%{int(player.volume * 100)}", inline=True)
        embed.add_field(name="Isteyen", value=requester_label(current), inline=True)
        if current.thumbnail:
            embed.set_thumbnail(url=current.thumbnail)
    else:
        embed.description = "Su an calan bir sarki yok."
        embed.add_field(name="Ses", value=f"%{int(player.volume * 100)}", inline=True)

    queue_preview = []
    for i, track in enumerate(player.queue[:10], 1):
        queue_preview.append(f"`{i}.` {track.display_title} - {requester_label(track)}")
    embed.add_field(name="Kuyruk", value="\n".join(queue_preview) if queue_preview else "Kuyruk bos.", inline=False)
    embed.add_field(name="Toplam Kuyruk", value=total_queue_duration(player), inline=True)
    embed.add_field(name="Otomatik Oneri", value="Acik" if player.autoplay else "Kapali", inline=True)
    repeat_labels = {"off": "Kapali", "track": "Sarki", "queue": "Kuyruk"}
    embed.add_field(name="Tekrar", value=repeat_labels.get(player.repeat_mode, "Kapali"), inline=True)
    backend = "Lavalink" if wavelink.Pool.nodes else "Lavalink bekleniyor"
    embed.add_field(name="Altyapi", value=backend, inline=True)
    embed.set_footer(text=f"{len(player.queue)} sarki sirada")
    return embed

def build_queue_embed(player: MusicPlayer):
    embed = discord.Embed(title="Kuyruk", color=0x3498DB)
    if player.current:
        embed.add_field(
            name="Simdi caliyor",
            value=f"**{player.current.display_title}**\nIsteyen: {requester_label(player.current)}",
            inline=False,
        )
    if not player.queue:
        embed.description = "Sirada sarki yok."
    else:
        lines = []
        for i, track in enumerate(player.queue[:10], 1):
            duration = format_duration(track.duration)
            lines.append(f"`{i}.` **{track.display_title}**\nSure: {duration} | Isteyen: {requester_label(track)}")
        if len(player.queue) > 10:
            lines.append(f"... ve {len(player.queue) - 10} sarki daha")
        embed.add_field(name="Siradaki sarkilar", value="\n".join(lines), inline=False)
    embed.add_field(name="Toplam sure", value=total_queue_duration(player), inline=True)
    embed.add_field(name="Sarki sayisi", value=str(len(player.queue)), inline=True)
    return embed

def build_history_embed(player: MusicPlayer):
    embed = discord.Embed(title="Gecmis", color=0x8E44AD)
    if not player.history:
        embed.description = "Henuz gecmis yok."
        return embed
    lines = []
    for i, track in enumerate(reversed(player.history[-20:]), 1):
        lines.append(f"`{i}.` **{track.display_title}**\nIsteyen: {requester_label(track)}")
    embed.description = "\n".join(lines)
    return embed

TEMP_MUSIC_MESSAGE_SECONDS = 4


async def delete_message_later(message, delay: float = TEMP_MUSIC_MESSAGE_SECONDS):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        pass


async def send_temporary_followup(interaction: discord.Interaction, content: str):
    message = await interaction.followup.send(
        content,
        ephemeral=True,
        wait=True,
    )
    asyncio.create_task(delete_message_later(message))
    return message


async def find_existing_music_panel(channel):
    if not bot.user:
        return None
    try:
        async for message in channel.history(limit=100):
            if message.author.id != bot.user.id or not message.embeds:
                continue
            if message.embeds[0].title == "Muzik Paneli":
                return message
    except (discord.Forbidden, discord.HTTPException):
        return None
    return None

async def update_music_panel(guild_id: int, move_to_latest: bool = False):
    player = get_player(guild_id)
    channel = bot.get_channel(player.text_channel_id) if player.text_channel_id else None
    if not channel:
        return
    embed = build_music_panel_embed(player)
    view = NowPlayingView(guild_id)
    message = None
    if player.panel_message_id:
        try:
            message = await channel.fetch_message(player.panel_message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            player.panel_message_id = None
            message = None
    if message is None:
        message = await find_existing_music_panel(channel)
        if message:
            player.panel_message_id = message.id
    if message and move_to_latest:
        try:
            await message.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass
        player.panel_message_id = None
        message = None
    if message:
        try:
            await message.edit(embed=embed, view=view)
            return
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            player.panel_message_id = None
    message = await channel.send(embed=embed, view=view)
    player.panel_message_id = message.id

@tasks.loop(seconds=30)
async def music_progress_task():
    for guild_id, player in list(players.items()):
        guild = bot.get_guild(guild_id)
        vc = guild.voice_client if guild else None
        if player.current and vc and (voice_is_playing(vc) or voice_is_paused(vc)):
            try:
                await update_music_panel(guild_id)
            except Exception as exc:
                print(f"Muzik panel ilerleme guncelleme hatasi: {exc}")

@music_progress_task.before_loop
async def before_music_progress_task():
    await bot.wait_until_ready()

def option_label(text: str, limit: int = 90):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "..."

class QueuePlaySelect(discord.ui.Select):
    def __init__(self, guild_id: int, queue: list[Track]):
        options = [
            discord.SelectOption(label=option_label(track.display_title), value=str(index), description=f"{index + 1}. siradan hemen cal")
            for index, track in enumerate(queue[:25])
        ]
        super().__init__(placeholder="Kuyruktan sarki sec ve hemen cal", min_values=1, max_values=1, options=options, row=1)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        player = get_player(self.guild_id)
        vc = interaction.guild.voice_client if interaction.guild else None
        index = int(self.values[0])
        async with player.lock:
            if index >= len(player.queue):
                await interaction.response.send_message("Bu sarki artik kuyrukta yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
                return
            selected = player.queue.pop(index)
            player.queue.insert(0, selected)
            player.skip_requested = True
        if vc and (voice_is_playing(vc) or voice_is_paused(vc)):
            await voice_stop(vc)
            await interaction.response.send_message("Secilen sarki siradaki parca olarak baslatiliyor.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        else:
            await interaction.response.defer(ephemeral=True)
            await play_next(interaction.guild)
        await update_music_panel(self.guild_id)

class QueueRemoveSelect(discord.ui.Select):
    def __init__(self, guild_id: int, queue: list[Track]):
        options = [
            discord.SelectOption(label=option_label(track.display_title), value=str(index), description=f"{index + 1}. siradan kaldir")
            for index, track in enumerate(queue[:25])
        ]
        super().__init__(placeholder="Kuyruktan sarki kaldir", min_values=1, max_values=1, options=options, row=2)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        player = get_player(self.guild_id)
        index = int(self.values[0])
        async with player.lock:
            if index >= len(player.queue):
                await interaction.response.send_message("Bu sarki artik kuyrukta yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
                return
            removed = player.queue.pop(index)
        await update_music_panel(self.guild_id)
        await interaction.response.send_message(f"Kuyruktan kaldirildi: {removed.display_title}", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

class RepeatModeSelect(discord.ui.Select):
    def __init__(self, guild_id: int, current_mode: str):
        options = [
            discord.SelectOption(label="Tekrar kapali", value="off", default=current_mode == "off"),
            discord.SelectOption(label="Sarkiyi tekrar et", value="track", default=current_mode == "track"),
            discord.SelectOption(label="Kuyrugu tekrar et", value="queue", default=current_mode == "queue"),
        ]
        super().__init__(placeholder="Tekrar modu sec", min_values=1, max_values=1, options=options, row=3)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        player = get_player(self.guild_id)
        player.repeat_mode = self.values[0]
        await update_music_panel(self.guild_id)
        labels = {"off": "Tekrar kapali", "track": "Sarki tekrar edilecek", "queue": "Kuyruk tekrar edilecek"}
        await interaction.response.send_message(labels[player.repeat_mode], ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

class PlaylistStartSelect(discord.ui.Select):
    def __init__(self, guild_id: int, playlists: dict):
        guild_playlists = playlists.get(str(guild_id), {})
        options = [
            discord.SelectOption(label=option_label(name), value=name, description=f"{len(items)} sarki")
            for name, items in list(guild_playlists.items())[:25]
        ]
        super().__init__(placeholder="Kayitli playlist baslat", min_values=1, max_values=1, options=options, row=4)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        player = get_player(self.guild_id)
        vc = interaction.guild.voice_client if interaction.guild else None
        playlists = load_music_playlists()
        items = playlists.get(str(self.guild_id), {}).get(self.values[0], [])
        if not items:
            await interaction.response.send_message("Playlist bos veya bulunamadi.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
            return
        tracks = [deserialize_track(item, interaction.user.id, interaction.user.display_name) for item in items]
        async with player.lock:
            player.queue.extend(tracks)
            should_start = not is_playback_active(player, vc)
            if should_start:
                player.starting = True
        await interaction.response.send_message(f"{len(tracks)} sarkilik playlist kuyruga eklendi: {self.values[0]}", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        schedule_queue_prefetch(self.guild_id)
        if should_start:
            await play_next(interaction.guild)
        await update_music_panel(self.guild_id)

class NowPlayingView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        player = get_player(guild_id)
        if player.queue:
            self.add_item(QueuePlaySelect(guild_id, player.queue))
            self.add_item(QueueRemoveSelect(guild_id, player.queue))
        self.add_item(RepeatModeSelect(guild_id, player.repeat_mode))
        playlists = load_music_playlists()
        if playlists.get(str(guild_id)):
            self.add_item(PlaylistStartSelect(guild_id, playlists))

    def _vc(self, interaction: discord.Interaction):
        return interaction.guild.voice_client if interaction.guild else None

    @discord.ui.button(label="Duraklat/Devam", style=discord.ButtonStyle.secondary, row=0, custom_id="music:pause_resume")
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self._vc(interaction)
        if not vc:
            await interaction.response.send_message("Ses kanalinda degilim.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        elif voice_is_paused(vc):
            player = get_player(self.guild_id)
            player.current_started_at = time.monotonic()
            player.paused_at = None
            await voice_pause(vc, False)
            await update_music_panel(self.guild_id)
            await interaction.response.send_message("Devam ediyor.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        elif voice_is_playing(vc):
            player = get_player(self.guild_id)
            player.current_elapsed_offset = current_position(player)
            player.paused_at = time.monotonic()
            await voice_pause(vc, True)
            await update_music_panel(self.guild_id)
            await interaction.response.send_message("Duraklatildi.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        else:
            await interaction.response.send_message("Su an calan bir sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

    @discord.ui.button(label="Atla", style=discord.ButtonStyle.primary, row=0, custom_id="music:skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self._vc(interaction)
        player = get_player(self.guild_id)
        if vc and (voice_is_playing(vc) or voice_is_paused(vc)):
            player.skip_requested = True
            await voice_stop(vc)
            await interaction.response.send_message("Atlandi.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        else:
            await interaction.response.send_message("Su an calan bir sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

    @discord.ui.button(label="Durdur", style=discord.ButtonStyle.danger, row=0, custom_id="music:stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await stop_music_player(interaction.guild)
        await update_music_panel(self.guild_id)
        await send_temporary_followup(interaction, "Muzik durduruldu ve ses kanalindan ayrildim.")

    @discord.ui.button(label="Ses -", style=discord.ButtonStyle.secondary, row=0, custom_id="music:volume_down")
    async def volume_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._change_volume(interaction, -0.1)

    @discord.ui.button(label="Ses +", style=discord.ButtonStyle.secondary, row=0, custom_id="music:volume_up")
    async def volume_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._change_volume(interaction, 0.1)

    async def _change_volume(self, interaction: discord.Interaction, delta: float):
        vc = self._vc(interaction)
        player = get_player(self.guild_id)
        player.volume = max(0.0, min(1.5, player.volume + delta))
        await voice_set_volume(vc, player.volume)
        await update_music_panel(self.guild_id)
        await interaction.response.send_message(f"Ses seviyesi: %{int(player.volume * 100)}", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

async def stop_music_player(guild):
    if not guild:
        return
    player = get_player(guild.id)
    vc = guild.voice_client
    async with player.lock:
        player.playback_generation += 1
        player.manual_disconnect = True
        player.skip_requested = False
        player.queue.clear()
        player.current = None
        player.starting = False
        player.mode = "music"
        player.current_started_at = None
        player.current_elapsed_offset = 0
        player.paused_at = None
        if player.prefetch_task and not player.prefetch_task.done():
            player.prefetch_task.cancel()
        player.prefetch_task = None
        if player.idle_task and not player.idle_task.done():
            player.idle_task.cancel()
        player.idle_task = None
    if vc:
        if voice_is_playing(vc) or voice_is_paused(vc):
            await voice_stop(vc)
        await vc.disconnect(force=True)

async def play_next(guild):
    player = get_player(guild.id)
    async with player.lock:
        vc = guild.voice_client
        if not player.queue or not vc:
            player.current = None
            player.starting = False
            if not player.queue:
                schedule_idle_disconnect(guild.id)
                await update_music_panel(guild.id)
            return
        item = player.queue.pop(0)
        player.starting = True
        player.skip_requested = False
        generation = player.playback_generation

    try:
        track = await resolve_queue_item(item)
        if not isinstance(track, Track):
            track = Track.url(track[0], track[1])
        playable = await resolve_lavalink_track(track)
    except Exception as e:
        print(f"Sarki yuklenemedi: {e}")
        channel = bot.get_channel(player.text_channel_id) if player.text_channel_id else None
        if channel:
            await channel.send(friendly_music_error(e))
        async with player.lock:
            player.current = None
            player.starting = False
        await play_next(guild)
        return

    async with player.lock:
        vc = guild.voice_client
        if not vc:
            player.current = None
            player.starting = False
            return
        if voice_is_playing(vc) or voice_is_paused(vc):
            player.queue.insert(0, track)
            player.starting = False
            return
        player.current = track
        seek_seconds = int(track.resume_at or 0)
        player.current_elapsed_offset = seek_seconds
        player.current_started_at = time.monotonic()
        player.paused_at = None
        track.resume_at = 0

    await vc.play(playable, start=max(0, seek_seconds) * 1000, volume=max(0, min(150, int(player.volume * 100))))
    async with player.lock:
        player.starting = False

    await update_music_panel(guild.id)
    schedule_queue_prefetch(guild.id)

async def handle_track_finished(guild, track: Track, error, generation: int):
    player = get_player(guild.id)
    async with player.lock:
        if generation != player.playback_generation:
            return
        if player.ignore_next_after:
            player.ignore_next_after = False
            return
    retry = False
    if error:
        print(f"Oynatma hatasi: {error}")
        retry = not player.skip_requested and track.attempts < 2
    needs_autoplay = False
    should_record_stat = False
    async with player.lock:
        if player.current is track:
            player.current = None
        player.current_started_at = None
        player.current_elapsed_offset = 0
        player.paused_at = None
        if retry:
            track.attempts += 1
            track.audio_url = None
            track.resolved = False
            player.queue.insert(0, track)
        elif not error:
            player.history.append(track)
            player.history = player.history[-50:]
            should_record_stat = True
            if not player.skip_requested and player.repeat_mode == "track" and track.source != "radio":
                track.audio_url = None
                track.resolved = False
                track.resume_at = 0
                player.queue.insert(0, track)
            elif not player.skip_requested and player.repeat_mode == "queue" and track.source != "radio":
                track.audio_url = None
                track.resolved = False
                track.resume_at = 0
                player.queue.append(track)
            elif player.autoplay and not player.queue and track.source != "radio":
                needs_autoplay = True
        player.skip_requested = False
    if needs_autoplay:
        autoplay_track = await pick_autoplay_track(player, track)
        if autoplay_track:
            async with player.lock:
                if player.autoplay and not player.queue and not player.skip_requested:
                    player.queue.append(autoplay_track)
        else:
            channel = bot.get_channel(player.text_channel_id) if player.text_channel_id else None
            if channel:
                await channel.send("Otomatik öneri için yeni bir şarkı bulamadım, aynı şarkıyı tekrar açmadım.")
    if should_record_stat:
        record_music_stat(guild.id, track)
    await play_next(guild)

async def idle_disconnect_later(guild_id: int):
    await asyncio.sleep(180)
    guild = bot.get_guild(guild_id)
    player = get_player(guild_id)
    vc = guild.voice_client if guild else None
    if not guild or not vc:
        return
    non_bot_members = [member for member in vc.channel.members if not member.bot]
    async with player.lock:
        should_leave = not non_bot_members and not player.queue and not player.current
        if should_leave:
            player.starting = False
            player.mode = "music"
    if should_leave:
        await vc.disconnect()
        await update_music_panel(guild_id)

def schedule_idle_disconnect(guild_id: int):
    player = get_player(guild_id)
    if player.idle_task and not player.idle_task.done():
        return
    player.idle_task = bot.loop.create_task(idle_disconnect_later(guild_id))

# ─────────────────────────────────────────────────────────────────────────────
#  FUTBOL YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_fd(endpoint, params={}):
    headers = {"X-Auth-Token": FD_KEY}
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{FD_URL}/{endpoint}", headers=headers, params=params) as r:
            if r.status != 200: return {}
            return await r.json()

async def fetch_apif(params):
    headers = {"x-apisports-key": APIF_KEY, "x-rapidapi-host": APIF_HOST}
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{APIF_URL}/fixtures", headers=headers, params=params) as r:
            if r.status != 200: return []
            data = await r.json()
            return data.get("response", [])

def utc_to_tr(utc_str):
    try:
        dt = datetime.datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        return dt.astimezone(TURKEY_TZ).strftime("%H:%M")
    except: return "?"

def format_fd_match(m):
    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]
    status = m["status"]
    score = m.get("score", {})
    home_g = score.get("fullTime", {}).get("home")
    away_g = score.get("fullTime", {}).get("away")
    half_h = score.get("halfTime", {}).get("home")
    half_a = score.get("halfTime", {}).get("away")
    if status == "FINISHED":
        return f"✅ `MS` {home} **{home_g} - {away_g}** {away}"
    elif status == "IN_PLAY":
        return f"⚽ **{home} {home_g} - {away_g} {away}**"
    elif status == "PAUSED":
        return f"☕ `HTD` **{home} {half_h} - {half_a} {away}**"
    elif status in ("TIMED", "SCHEDULED"):
        return f"🕐 `{utc_to_tr(m.get('utcDate', ''))}` {home} vs {away}"
    elif status == "POSTPONED":
        return f"📅 `ERL` {home} vs {away}"
    elif status == "CANCELLED":
        return f"❌ `İPT` {home} vs {away}"
    return f"❓ {home} vs {away}"

def format_apif_match(f):
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    status = f["fixture"]["status"]["short"]
    home_g = f["goals"]["home"]
    away_g = f["goals"]["away"]
    elapsed = f["fixture"]["status"]["elapsed"]
    if status in LIVE_STATUSES_APIF and status != "HT":
        return f"⚽ `{elapsed}'` **{home} {home_g} - {away_g} {away}**"
    elif status == "HT":
        return f"☕ `HTD` **{home} {home_g} - {away_g} {away}**"
    elif status in ("FT", "AET", "PEN"):
        return f"✅ `MS` {home} **{home_g} - {away_g}** {away}"
    elif status == "NS":
        dt = datetime.datetime.fromtimestamp(f["fixture"]["timestamp"], tz=TURKEY_TZ)
        return f"🕐 `{dt.strftime('%H:%M')}` {home} vs {away}"
    elif status == "PST":
        return f"📅 `ERL` {home} vs {away}"
    elif status == "CANC":
        return f"❌ `İPT` {home} vs {away}"
    return f"❓ {home} vs {away}"

async def build_daily_embed():
    today = date.today().strftime("%Y-%m-%d")
    today_str = date.today().strftime("%d.%m.%Y")
    embed = discord.Embed(title=f"📅  {today_str} — Günün Maçları", color=0x2b2d42)
    embed.set_footer(text="Hoşlaf Bot • Saat: Türkiye (UTC+3)")
    has_any = False
    for key, league in FD_LEAGUES.items():
        data = await fetch_fd(f"competitions/{league['code']}/matches", {"dateFrom": today, "dateTo": today})
        matches = data.get("matches", [])
        if matches:
            has_any = True
            lines = [format_fd_match(m) for m in matches]
            embed.add_field(name=f"{league['emoji']}  {league['name']}", value="\n".join(lines), inline=False)
    if not has_any:
        embed.description = "Bugün seçili liglerde maç bulunmuyor."
    return embed, has_any

async def build_live_embed():
    all_raw = await fetch_apif({"live": "all"})
    fixtures = [f for f in all_raw if f["league"]["id"] in APIF_ALL_IDS]
    now_str = datetime.datetime.now(TURKEY_TZ).strftime("%H:%M:%S")
    embed = discord.Embed(title="🔴  Canlı Maçlar", color=0xe63946)
    embed.set_footer(text=f"Sorgulandı: {now_str} • Hoşlaf Bot")
    if not fixtures:
        embed.description = "Şu an oynanan maç yok."
        return embed, False
    grouped = {}
    for f in fixtures:
        lid = f["league"]["id"]
        lname = f["league"]["name"]
        emoji = LEAGUE_EMOJIS.get(lid, "🏆")
        key = f"{emoji}  {lname}"
        grouped.setdefault(key, []).append(f)
    for lname, matches in grouped.items():
        embed.add_field(name=lname, value="\n".join(format_apif_match(f) for f in matches), inline=False)
    return embed, True

async def build_standings_embed(league_key):
    league = FD_LEAGUES[league_key]
    data = await fetch_fd(f"competitions/{league['code']}/standings")
    standings = data.get("standings", [])
    embed = discord.Embed(title=f"{league['emoji']}  {league['name']} — Puan Durumu", color=0x2b2d42)
    embed.set_footer(text="Hoşlaf Bot • football-data.org")
    for group in standings:
        if group.get("type") == "TOTAL":
            table = group.get("table", [])
            lines = []
            for row in table:
                pos = row["position"]
                team = row["team"]["name"]
                pts = row["points"]
                w, d, l = row["won"], row["draw"], row["lost"]
                gd = row["goalDifference"]
                gd_str = f"+{gd}" if gd > 0 else str(gd)
                lines.append(f"`{pos:2}.` **{team}** — {pts} puan ({w}G {d}B {l}M) AV:{gd_str}")
            if lines:
                embed.description = "\n".join(lines)
            break
    return embed

async def build_bracket_embed(comp_code, comp_name, emoji):
    embed = discord.Embed(title=f"{emoji}  {comp_name} — Turnuva Ağacı", color=0xffd700)
    embed.set_footer(text="Hoşlaf Bot • football-data.org")
    stages = ["PLAYOFFS", "LAST_16", "ROUND_OF_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL"]
    async with aiohttp.ClientSession() as s:
        for stage in stages:
            async with s.get(
                f"{FD_URL}/competitions/{comp_code}/matches",
                headers={"X-Auth-Token": FD_KEY},
                params={"stage": stage}
            ) as r:
                if r.status != 200: continue
                data = await r.json()
                matches = data.get("matches", [])
                if not matches: continue
                stage_label = STAGE_NAMES.get(stage, stage)
                pairs = {}
                for m in matches:
                    h = m["homeTeam"]["name"]
                    a = m["awayTeam"]["name"]
                    key = tuple(sorted([h, a]))
                    pairs.setdefault(key, []).append(m)
                lines = []
                for key, pair in pairs.items():
                    pair.sort(key=lambda x: x["utcDate"])
                    t1 = pair[0]["homeTeam"]["name"]
                    t2 = pair[0]["awayTeam"]["name"]
                    lines.append(f"**{t1}** vs **{t2}**")
                    for i, m in enumerate(pair):
                        sh = m["score"]["fullTime"]["home"]
                        sa = m["score"]["fullTime"]["away"]
                        skor = f"{sh}-{sa}" if sh is not None else "?-?"
                        icon = "✅" if m["status"] == "FINISHED" else "🕐"
                        leg = f"{i+1}. Maç" if len(pair) > 1 else "Maç"
                        lines.append(f"  {icon} {leg}: `{skor}`")
                    lines.append("")
                if lines:
                    embed.add_field(name=stage_label, value="\n".join(lines).strip(), inline=False)
    return embed

# ─────────────────────────────────────────────────────────────────────────────
#  EXA YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────

async def exa_search(query, num_results=5):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": EXA_API_KEY, "Content-Type": "application/json"},
            json={"query": query, "numResults": num_results, "contents": {"text": {"maxCharacters": 300}}}
        ) as resp:
            if resp.status != 200: return []
            data = await resp.json()
            return data.get("results", [])

async def exa_turkiye_haberleri():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": EXA_API_KEY, "Content-Type": "application/json"},
            json={"query": "Türkiye gündem son dakika haberleri", "numResults": 10, "contents": {"text": {"maxCharacters": 200}}}
        ) as resp:
            if resp.status != 200: return []
            data = await resp.json()
            return data.get("results", [])

# ─────────────────────────────────────────────────────────────────────────────
#  ZAMANLANMIŞ GÖREVLER
# ─────────────────────────────────────────────────────────────────────────────

@tasks.loop(time=HABER_SAATI)
async def gunluk_haber():
    kanal = bot.get_channel(HABER_KANAL_ID)
    if not kanal: return
    haberler = await exa_turkiye_haberleri()
    if not haberler:
        await kanal.send("❌ Bugün haber çekilemedi.")
        return
    tarih = datetime.datetime.utcnow().strftime("%d.%m.%Y")
    embed = discord.Embed(title=f"📰 Türkiye Gündemi — {tarih}", color=0xe74c3c, timestamp=datetime.datetime.utcnow())
    for i, haber in enumerate(haberler[:10], 1):
        baslik = haber.get("title", "Başlık yok")
        url = haber.get("url", "")
        ozet = haber.get("text", "").strip()
        if len(ozet) > 150: ozet = ozet[:150] + "…"
        embed.add_field(name=f"{i}. {baslik}", value=f"{ozet}\n[🔗 Habere git]({url})" if url else ozet, inline=False)
    embed.set_footer(text="Kaynak: Exa AI")
    await kanal.send(embed=embed)

@gunluk_haber.before_loop
async def before_gunluk_haber():
    await bot.wait_until_ready()

@tasks.loop(minutes=1)
async def daily_schedule_task():
    now = datetime.datetime.now(TURKEY_TZ)
    if now.hour == 0 and now.minute == 1:
        kanal = bot.get_channel(FUTBOL_KANAL_ID)
        if kanal is None: return
        embed, has = await build_daily_embed()
        if has:
            await kanal.send(embed=embed)

@daily_schedule_task.before_loop
async def before_daily_schedule():
    await bot.wait_until_ready()

# ─────────────────────────────────────────────────────────────────────────────
#  EVENTS
# ─────────────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"Hoslaf Bot hazir! {bot.user}")

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"Lavalink node hazir: {payload.node.identifier}")

@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    if not payload.player or not payload.player.guild:
        return
    guild = payload.player.guild
    player = get_player(guild.id)
    track = player.current
    if not track:
        return
    await handle_track_finished(guild, track, None, player.playback_generation)

@bot.event
async def on_wavelink_track_exception(payload: wavelink.TrackExceptionEventPayload):
    if not payload.player or not payload.player.guild:
        return
    guild = payload.player.guild
    player = get_player(guild.id)
    track = player.current
    if not track:
        return
    await handle_track_finished(guild, track, payload.exception, player.playback_generation)

@bot.event
async def on_wavelink_track_stuck(payload: wavelink.TrackStuckEventPayload):
    if not payload.player or not payload.player.guild:
        return
    guild = payload.player.guild
    player = get_player(guild.id)
    track = player.current
    if not track:
        return
    await handle_track_finished(guild, track, RuntimeError("Lavalink track stuck"), player.playback_generation)

@bot.event
async def on_voice_state_update(member, before, after):
    if not bot.user or not member.guild:
        return
    if member.id != bot.user.id:
        player = get_player(member.guild.id)
        vc = member.guild.voice_client
        if vc and after.channel == vc.channel and player.idle_task and not player.idle_task.done():
            player.idle_task.cancel()
        if vc and before.channel == vc.channel:
            non_bot_members = [voice_member for voice_member in vc.channel.members if not voice_member.bot]
            if not non_bot_members:
                schedule_idle_disconnect(member.guild.id)
        return

    player = get_player(member.guild.id)
    if after.channel:
        player.voice_channel_id = after.channel.id
        return
    if not before.channel or player.manual_disconnect or player.skip_requested:
        return

    track_to_resume = None
    async with player.lock:
        if player.mode == "music" and player.current:
            track_to_resume = player.current
            track_to_resume.resume_at = current_position(player)
            track_to_resume.audio_url = None
            track_to_resume.resolved = False
            player.queue.insert(0, track_to_resume)
            player.current = None
            player.starting = True
            player.current_started_at = None
            player.current_elapsed_offset = 0
            player.paused_at = None
        elif player.mode != "music":
            player.current = None

    if track_to_resume:
        await asyncio.sleep(3)
        try:
            player.voice_channel_id = before.channel.id
            await ensure_voice_player(member.guild, before.channel)
            await play_next(member.guild)
        except Exception as exc:
            print(f"Voice reconnect failed: {exc}")

# ─────────────────────────────────────────────────────────────────────────────
#  MÜZİK KOMUTLARI
# ─────────────────────────────────────────────────────────────────────────────

@bot.tree.command(name="oynat", description="Sarki adi, YouTube/Spotify/SoundCloud linki veya playlist cal")
@app_commands.describe(sarki="Sarki adi, YouTube linki, Spotify linki veya playlist linki")
async def oynat(interaction: discord.Interaction, sarki: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Bir ses kanalinda olman gerekiyor!", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return

    voice_channel = interaction.user.voice.channel
    guild = interaction.guild
    player = get_player(guild.id)
    await interaction.response.defer(ephemeral=True)

    player.text_channel_id = interaction.channel.id
    player.voice_channel_id = voice_channel.id
    player.manual_disconnect = False
    try:
        vc = await ensure_voice_player(guild, voice_channel)
    except Exception as exc:
        await send_temporary_followup(interaction, f"Lavalink hazir degil: {exc}")
        return

    try:
        tracks: list[Track] = []
        start_message = None
        queue_message = None
        requester_id = interaction.user.id
        requester_name = interaction.user.display_name

        if is_spotify_playlist_url(sarki) or is_spotify_album_url(sarki):
            queries = await spotify_playlist_to_queries(sarki)
            if not queries:
                await send_temporary_followup(interaction, "Playlist bos veya bulunamadi.")
                return
            tracks = [Track.search(q, requester_id, requester_name) for q in queries]
            start_message = f"{len(tracks)} sarkilik Spotify playlist basliyor."
            queue_message = f"{len(tracks)} sarki kuyruga eklendi."
        elif is_spotify_url(sarki):
            query = await spotify_to_search_query(sarki)
            tracks = [Track.search(query, requester_id, requester_name)]
            start_message = f"Basliyor: {query}"
            queue_message = f"{query} kuyruga eklendi."
        elif is_url(sarki) and is_playlist_url(sarki):
            playlist_tracks = await fetch_playlist_yt(sarki)
            if not playlist_tracks:
                await send_temporary_followup(interaction, "Playlist bos veya bulunamadi.")
                return
            tracks = [Track.url(video_url, title, requester_id, requester_name) for video_url, title in playlist_tracks]
            start_message = f"{len(tracks)} sarkilik YouTube playlist basliyor."
            queue_message = f"{len(tracks)} sarki kuyruga eklendi."
        elif is_url(sarki):
            tracks = [Track.url(sarki, requester_id=requester_id, requester_name=requester_name)]
            start_message = "Link basliyor."
            queue_message = "Link kuyruga eklendi."
        else:
            tracks = [Track.search(sarki, requester_id, requester_name)]
            start_message = f"Basliyor: {sarki}"
            queue_message = f"{sarki} kuyruga eklendi."

        async with player.lock:
            active = is_playback_active(player, vc)
            player.mode = "music"
            if player.idle_task and not player.idle_task.done():
                player.idle_task.cancel()
            if active:
                player.queue.extend(tracks)
                position = len(player.queue) - len(tracks) + 1
            else:
                player.starting = True
                player.queue.extend(tracks)
                position = 1

        schedule_queue_prefetch(guild.id)
        if active:
            suffix = f" (Pozisyon: {position})" if len(tracks) == 1 else ""
            await send_temporary_followup(interaction, queue_message + suffix)
        else:
            await send_temporary_followup(interaction, start_message)
            await play_next(guild)
        await update_music_panel(guild.id, move_to_latest=True)
    except Exception as e:
        async with player.lock:
            player.starting = False
        await send_temporary_followup(interaction, friendly_music_error(e))

@bot.tree.command(name="kapat", description="Sarkiyi kapatir ve ses kanalindan ayrilir")
async def kapat(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    had_voice = interaction.guild.voice_client is not None
    await stop_music_player(interaction.guild)
    await update_music_panel(interaction.guild.id)
    message = "Muzik kapatildi ve ses kanalindan ayrildim." if had_voice else "Zaten bir ses kanalinda degilim."
    await send_temporary_followup(interaction, message)

@bot.tree.command(name="atla", description="Sarkiyi atlar")
@app_commands.describe(miktar="Kac sarki atlanacak (varsayilan 1)")
async def atla(interaction: discord.Interaction, miktar: int = 1):
    vc = interaction.guild.voice_client
    player = get_player(interaction.guild.id)
    if not vc or (not voice_is_playing(vc) and not voice_is_paused(vc)):
        await interaction.response.send_message("Su an calan bir sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return
    async with player.lock:
        del player.queue[:min(max(miktar - 1, 0), len(player.queue))]
        player.skip_requested = True
    await voice_stop(vc)
    await interaction.response.send_message(f"{miktar} sarki atlandi!" if miktar > 1 else "Atlandi!", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

@bot.tree.command(name="duraklat", description="Sarkiyi duraklatir")
async def duraklat(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and voice_is_playing(vc):
        player = get_player(interaction.guild.id)
        player.current_elapsed_offset = current_position(player)
        player.paused_at = time.monotonic()
        await voice_pause(vc, True)
        await update_music_panel(interaction.guild.id)
        await interaction.response.send_message("Duraklatildi!", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
    else:
        await interaction.response.send_message("Su an calan bir sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

@bot.tree.command(name="devam", description="Duraklatilan sarkiyi devam ettirir")
async def devam(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and voice_is_paused(vc):
        player = get_player(interaction.guild.id)
        player.current_started_at = time.monotonic()
        player.paused_at = None
        await voice_pause(vc, False)
        await update_music_panel(interaction.guild.id)
        await interaction.response.send_message("Devam ediliyor!", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
    else:
        await interaction.response.send_message("Duraklatilmis bir sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

@bot.tree.command(name="sardir", description="Sarkiyi belirtilen saniyeye sarar")
@app_commands.describe(saniye="Kacinci saniyeye sarilacak")
async def sardir(interaction: discord.Interaction, saniye: int):
    vc = interaction.guild.voice_client
    player = get_player(interaction.guild.id)
    if not vc or (not voice_is_playing(vc) and not voice_is_paused(vc)) or not player.current:
        await interaction.response.send_message("Su an calan bir sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return
    guild = interaction.guild
    await interaction.response.defer()
    try:
        async with player.lock:
            player.skip_requested = False
            player.current_elapsed_offset = max(0, int(saniye))
            player.current_started_at = time.monotonic()
            player.paused_at = None
        if is_lavalink_player(vc):
            await vc.seek(max(0, int(saniye)) * 1000)
        else:
            raise RuntimeError("Bu komut Lavalink player gerektiriyor.")
        dakika, sn = divmod(saniye, 60)
        await update_music_panel(interaction.guild.id)
        await interaction.followup.send(f"{dakika:02d}:{sn:02d} saniyesine sarildi!")
    except Exception as e:
        await interaction.followup.send(f"Hata: {e}")

@bot.tree.command(name="karistir", description="Oynatma listesini karistirir")
async def karistir(interaction: discord.Interaction):
    player = get_player(interaction.guild.id)
    if not player.queue:
        await interaction.response.send_message("Kuyruk zaten bos.", ephemeral=True)
        return
    async with player.lock:
        random.shuffle(player.queue)
    await interaction.response.send_message(f"{len(player.queue)} sarki karistirildi!")

@bot.tree.command(name="ses", description="Ses seviyesini ayarla (0-100)")
@app_commands.describe(seviye="Ses seviyesi (0-100)")
async def ses(interaction: discord.Interaction, seviye: int):
    vc = interaction.guild.voice_client
    player = get_player(interaction.guild.id)
    player.volume = max(0, min(seviye, 100)) / 100
    if vc:
        await voice_set_volume(vc, player.volume)
        await interaction.response.send_message(f"Ses seviyesi: **{seviye}%**")
    else:
        await interaction.response.send_message(f"Ses seviyesi kaydedildi: **{seviye}%**")

@bot.tree.command(name="kuyruk", description="Kuyrugu goster")
async def kuyruk_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(embed=build_queue_embed(get_player(interaction.guild.id)))

@bot.tree.command(name="playlistkaydet", description="Mevcut muzik kuyrugunu sunucu playlisti olarak kaydeder")
@app_commands.describe(ad="Playlist adi")
async def playlistkaydet(interaction: discord.Interaction, ad: str):
    player = get_player(interaction.guild.id)
    tracks = ([player.current] if player.current else []) + list(player.queue)
    tracks = [track for track in tracks if isinstance(track, Track)]
    if not tracks:
        await interaction.response.send_message("Kaydedilecek sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return
    playlists = load_music_playlists()
    guild_playlists = playlists.setdefault(str(interaction.guild.id), {})
    safe_name = option_label(ad, 60)
    guild_playlists[safe_name] = [serialize_track(track) for track in tracks[:100]]
    save_music_playlists(playlists)
    await update_music_panel(interaction.guild.id)
    await interaction.response.send_message(f"Playlist kaydedildi: {safe_name} ({len(guild_playlists[safe_name])} sarki)", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

@bot.tree.command(name="playlistler", description="Sunucudaki kayitli muzik playlistlerini gosterir")
async def playlistler(interaction: discord.Interaction):
    playlists = load_music_playlists().get(str(interaction.guild.id), {})
    if not playlists:
        await interaction.response.send_message("Bu sunucuda kayitli playlist yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return
    lines = [f"`{name}` - {len(items)} sarki" for name, items in playlists.items()]
    await interaction.response.send_message("\n".join(lines[:25]), ephemeral=True)

@bot.tree.command(name="playlistsil", description="Sunucu playlistini siler")
@app_commands.describe(ad="Silinecek playlist adi")
async def playlistsil(interaction: discord.Interaction, ad: str):
    playlists = load_music_playlists()
    guild_playlists = playlists.get(str(interaction.guild.id), {})
    if ad not in guild_playlists:
        await interaction.response.send_message("Bu isimde playlist bulunamadi.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return
    guild_playlists.pop(ad, None)
    save_music_playlists(playlists)
    await update_music_panel(interaction.guild.id)
    await interaction.response.send_message(f"Playlist silindi: {ad}", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

@bot.tree.command(name="gecmis", description="Son calinan sarkilari goster")
async def gecmis(interaction: discord.Interaction):
    await interaction.response.send_message(embed=build_history_embed(get_player(interaction.guild.id)))

@bot.tree.command(name="otomatik", description="Kuyruk bitince otomatik oneriyi acar veya kapatir")
@app_commands.describe(durum="ac veya kapat")
@app_commands.choices(durum=[
    app_commands.Choice(name="Ac", value="ac"),
    app_commands.Choice(name="Kapat", value="kapat"),
])
async def otomatik(interaction: discord.Interaction, durum: str):
    player = get_player(interaction.guild.id)
    player.autoplay = durum == "ac"
    await update_music_panel(interaction.guild.id)
    await interaction.response.send_message("Otomatik oneri acildi." if player.autoplay else "Otomatik oneri kapatildi.")

@bot.tree.command(name="tekrar", description="Muzik tekrar modunu ayarlar")
@app_commands.describe(mod="Tekrar modu")
@app_commands.choices(mod=[
    app_commands.Choice(name="Kapali", value="off"),
    app_commands.Choice(name="Sarki", value="track"),
    app_commands.Choice(name="Kuyruk", value="queue"),
])
async def tekrar(interaction: discord.Interaction, mod: str):
    player = get_player(interaction.guild.id)
    player.repeat_mode = mod
    await update_music_panel(interaction.guild.id)
    labels = {"off": "Tekrar kapatildi.", "track": "Calan sarki tekrar edilecek.", "queue": "Kuyruk tekrar edilecek."}
    await interaction.response.send_message(labels.get(mod, "Tekrar modu guncellendi."), ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)

@bot.tree.command(name="muzikprofil", description="Muzik istatistiklerini goster")
async def muzikprofil(interaction: discord.Interaction):
    stats = load_music_stats()
    key = f"{interaction.guild.id}:{interaction.user.id}"
    user = stats.get("users", {}).get(key)
    embed = discord.Embed(title=f"Muzik Profili - {interaction.user.display_name}", color=0x2ECC71)
    if not user:
        embed.description = "Henuz muzik istatistigin yok."
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    embed.add_field(name="Eklenen sarki", value=str(user.get("tracks", 0)), inline=True)
    embed.add_field(name="Toplam sure", value=format_duration(user.get("duration", 0)), inline=True)
    top_tracks = sorted(user.get("top_tracks", {}).items(), key=lambda item: item[1], reverse=True)[:5]
    top_artists = sorted(user.get("top_artists", {}).items(), key=lambda item: item[1], reverse=True)[:5]
    embed.add_field(
        name="En cok ekledigin sarkilar",
        value="\n".join(f"`{count}x` {title}" for title, count in top_tracks) if top_tracks else "Yok",
        inline=False,
    )
    embed.add_field(
        name="En cok ekledigin sanatci/kanal",
        value="\n".join(f"`{count}x` {artist}" for artist, count in top_artists) if top_artists else "Yok",
        inline=False,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="lyrics", description="Su an calan sarkinin sozlerini gosterir")
async def lyrics(interaction: discord.Interaction):
    title = get_current_title(interaction.guild.id)
    if not title:
        await interaction.response.send_message("Su an calan bir sarki yok.", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return
    await interaction.response.defer()
    try:
        loop = asyncio.get_event_loop()
        song = await loop.run_in_executor(executor, lambda: genius.search_song(title))
        if not song:
            await interaction.followup.send(f"**{title}** icin sarki sozu bulunamadi.")
            return
        lyrics_text = song.lyrics
        if "EmbedShare" in lyrics_text:
            lyrics_text = lyrics_text[:lyrics_text.rfind("EmbedShare")]
        header = f"**{song.title}** - {song.artist}\n\n"
        max_len = 1990 - len(header)
        if len(lyrics_text) <= max_len:
            await interaction.followup.send(header + lyrics_text)
        else:
            await interaction.followup.send(header + lyrics_text[:max_len] + "...")
            remaining = lyrics_text[max_len:]
            while remaining:
                chunk = remaining[:1990]
                remaining = remaining[1990:]
                await interaction.channel.send(chunk + ("..." if remaining else ""))
    except Exception as e:
        await interaction.followup.send(f"Sarki sozleri alinamadi: {e}")

@bot.tree.command(name="ara", description="Exa AI ile web'de arama yap")
@app_commands.describe(sorgu="Arama sorgusu")
async def ara(interaction: discord.Interaction, sorgu: str):
    await interaction.response.defer()
    try:
        sonuclar = await exa_search(sorgu, num_results=5)
        if not sonuclar:
            await interaction.followup.send("❌ Sonuç bulunamadı.")
            return
        embed = discord.Embed(title=f"🔍 Arama: {sorgu}", color=0x3498db, timestamp=datetime.datetime.utcnow())
        for i, s in enumerate(sonuclar, 1):
            baslik = s.get("title", "Başlık yok")
            url = s.get("url", "")
            ozet = s.get("text", "").strip()
            if len(ozet) > 200: ozet = ozet[:200] + "…"
            embed.add_field(name=f"{i}. {baslik}", value=f"{ozet}\n[🔗 Bağlantı]({url})" if url else ozet, inline=False)
        embed.set_footer(text="Kaynak: Exa AI")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Arama hatası: {e}")

@bot.tree.command(name="haber", description="Türkiye gündeminden anlık haberler getirir")
async def haber(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        haberler = await exa_turkiye_haberleri()
        if not haberler:
            await interaction.followup.send("❌ Haber çekilemedi.")
            return
        tarih = datetime.datetime.utcnow().strftime("%d.%m.%Y")
        embed = discord.Embed(title=f"📰 Türkiye Gündemi — {tarih}", color=0xe74c3c, timestamp=datetime.datetime.utcnow())
        for i, h in enumerate(haberler[:10], 1):
            baslik = h.get("title", "Başlık yok")
            url = h.get("url", "")
            ozet = h.get("text", "").strip()
            if len(ozet) > 150: ozet = ozet[:150] + "…"
            embed.add_field(name=f"{i}. {baslik}", value=f"{ozet}\n[🔗 Habere git]({url})" if url else ozet, inline=False)
        embed.set_footer(text="Kaynak: Exa AI")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Hata: {e}")

# ─────────────────────────────────────────────────────────────────────────────
#  FUTBOL KOMUTLARI
# ─────────────────────────────────────────────────────────────────────────────

@bot.tree.command(name="bugun", description="Bugünkü maç takvimini gösterir")
async def cmd_bugun(interaction: discord.Interaction):
    await interaction.response.defer()
    embed, _ = await build_daily_embed()
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="canli", description="Şu an oynanan maçların canlı skorlarını gösterir")
async def cmd_canli(interaction: discord.Interaction):
    await interaction.response.defer()
    embed, _ = await build_live_embed()
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="lig", description="Belirli bir ligin bugünkü maçlarını gösterir")
@app_commands.describe(lig="Lig seçin")
@app_commands.choices(lig=[
    app_commands.Choice(name="Premier League",   value="premier"),
    app_commands.Choice(name="La Liga",          value="laliga"),
    app_commands.Choice(name="Bundesliga",       value="bundesliga"),
    app_commands.Choice(name="Serie A",          value="seriea"),
    app_commands.Choice(name="Ligue 1",          value="ligue1"),
    app_commands.Choice(name="Sampiyonlar Ligi", value="ucl"),
])
async def cmd_lig(interaction: discord.Interaction, lig: str):
    await interaction.response.defer()
    today = date.today().strftime("%Y-%m-%d")
    league = FD_LEAGUES[lig]
    data = await fetch_fd(f"competitions/{league['code']}/matches", {"dateFrom": today, "dateTo": today})
    matches = data.get("matches", [])
    embed = discord.Embed(
        title=f"{league['emoji']}  {league['name']} — {date.today().strftime('%d.%m.%Y')}",
        color=0x2b2d42
    )
    embed.set_footer(text="Hoşlaf Bot • Saat: Türkiye (UTC+3)")
    embed.description = "\n".join(format_fd_match(m) for m in matches) if matches else "Bugün bu ligde maç yok."
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="puandurumu", description="Lig puan durumunu gösterir")
@app_commands.describe(lig="Lig seçin")
@app_commands.choices(lig=[
    app_commands.Choice(name="Premier League",   value="premier"),
    app_commands.Choice(name="La Liga",          value="laliga"),
    app_commands.Choice(name="Bundesliga",       value="bundesliga"),
    app_commands.Choice(name="Serie A",          value="seriea"),
    app_commands.Choice(name="Ligue 1",          value="ligue1"),
])
async def cmd_puan(interaction: discord.Interaction, lig: str):
    await interaction.response.defer()
    embed = await build_standings_embed(lig)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="turnuva", description="Şampiyonlar Ligi turnuva ağacını gösterir")
async def cmd_turnuva(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = await build_bracket_embed("CL", "Şampiyonlar Ligi", "⭐")
    await interaction.followup.send(embed=embed)

# ─────────────────────────────────────────────────────────────────────────────
#  WİKİPEDİA YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────

AY_ADLARI_TR = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]

async def wikipedia_getir(ay: int, gun: int):
    headers = {"Accept": "application/json", "User-Agent": "HoslafBot/1.0 (Discord Bot)"}
    async with aiohttp.ClientSession() as session:
        tr_url = f"https://tr.wikipedia.org/api/rest_v1/feed/onthisday/events/{ay:02d}/{gun:02d}"
        async with session.get(tr_url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                olaylar = data.get("events", [])
                if olaylar:
                    return olaylar, "tr"
        en_url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{ay:02d}/{gun:02d}"
        async with session.get(en_url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                olaylar = data.get("events", [])
                if olaylar:
                    return olaylar, "en"
    return [], None

def wiki_embed_olustur(olaylar, ay, gun, dil):
    dil_notu = "" if dil == "tr" else " *(İngilizce)*"
    embed = discord.Embed(
        title=f"📅 Tarihte Bugün — {gun} {AY_ADLARI_TR[ay]}{dil_notu}",
        color=discord.Color.from_rgb(180, 60, 60),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="Kaynak: Wikipedia", icon_url="https://www.wikipedia.org/static/favicon/wikipedia.ico")
    secilen = random.sample(olaylar, min(WIKI_OLAY_SAYISI, len(olaylar)))
    secilen.sort(key=lambda e: e.get("year", 0))
    for olay in secilen:
        yil = olay.get("year", "?")
        metin = olay.get("text", "Açıklama yok.")
        link = ""
        sayfalar = olay.get("pages", [])
        if sayfalar:
            link_url = sayfalar[0].get("content_urls", {}).get("desktop", {}).get("page", "")
            if link_url:
                link = f"\n🔗 [Vikipedi'de oku]({link_url})"
        embed.add_field(name=f"**{yil}**", value=metin[:512] + link, inline=False)
    return embed

# ─── Wikipedia Günlük Görev ───────────────────────────────────────────────────

@tasks.loop(time=WIKI_SAATI)
async def gunluk_wiki():
    kanal = bot.get_channel(WIKI_KANAL_ID)
    if not kanal:
        print(f"[HATA] Wiki kanalı bulunamadı: {WIKI_KANAL_ID}")
        return
    bugun = datetime.date.today()
    olaylar, dil = await wikipedia_getir(bugun.month, bugun.day)
    if not olaylar:
        await kanal.send("⚠️ Bugün için Wikipedia'dan olay alınamadı.")
        return
    embed = wiki_embed_olustur(olaylar, bugun.month, bugun.day, dil)
    await kanal.send(embed=embed)

@gunluk_wiki.before_loop
async def before_gunluk_wiki():
    await bot.wait_until_ready()

# ─── Wikipedia Komutları ──────────────────────────────────────────────────────

@bot.tree.command(name="tarihtebugun", description="Bugün tarihte ne oldu?")
async def tarihtebugun(interaction: discord.Interaction):
    await interaction.response.defer()
    bugun = datetime.date.today()
    olaylar, dil = await wikipedia_getir(bugun.month, bugun.day)
    if not olaylar:
        await interaction.followup.send("⚠️ Bugün için Wikipedia'dan olay alınamadı.")
        return
    embed = wiki_embed_olustur(olaylar, bugun.month, bugun.day, dil)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="tarihsorgu", description="Belirli bir tarihteki olayları gösterir")
@app_commands.describe(ay="Ay (1-12)", gun="Gün (1-31)")
async def tarihsorgu(interaction: discord.Interaction, ay: int, gun: int):
    await interaction.response.defer()
    try:
        datetime.date(datetime.date.today().year, ay, gun)
    except ValueError:
        await interaction.followup.send("❌ Geçersiz tarih.")
        return
    olaylar, dil = await wikipedia_getir(ay, gun)
    if not olaylar:
        await interaction.followup.send("⚠️ Bu tarih için Wikipedia'dan olay alınamadı.")
        return
    embed = wiki_embed_olustur(olaylar, ay, gun, dil)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="rastgeletarih", description="Rastgele bir tarihteki olayları gösterir")
async def rastgeletarih(interaction: discord.Interaction):
    await interaction.response.defer()
    rastgele_ay = random.randint(1, 12)
    gun_max = (datetime.date(2024, rastgele_ay % 12 + 1, 1) - datetime.timedelta(days=1)).day
    rastgele_gun = random.randint(1, gun_max)
    olaylar, dil = await wikipedia_getir(rastgele_ay, rastgele_gun)
    if not olaylar:
        await interaction.followup.send("⚠️ Olay alınamadı, tekrar dene.")
        return
    embed = wiki_embed_olustur(olaylar, rastgele_ay, rastgele_gun, dil)
    await interaction.followup.send(embed=embed)

# ─────────────────────────────────────────────────────────────────────────────
#  RADYO
# ─────────────────────────────────────────────────────────────────────────────

async def radyo_ara(isim: str) -> list[dict]:
    """Radio Browser API ile radyo ara."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://de1.api.radio-browser.info/json/stations/byname/" + isim,
            headers={"User-Agent": "HoslafBot/1.0"},
            params={"limit": 10, "hidebroken": "true", "order": "clickcount", "reverse": "true"}
        ) as resp:
            if resp.status != 200:
                return []
            return await resp.json()


@bot.tree.command(name="radyo", description="Radyo yayini baslatir. Radyo adi yazarak arayabilirsin.")
@app_commands.describe(isim="Radyo adi (orn: Kral FM, TRT Radyo 1, Power FM)")
async def radyo(interaction: discord.Interaction, isim: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Bir ses kanalinda olman gerekiyor!", ephemeral=True, delete_after=TEMP_MUSIC_MESSAGE_SECONDS)
        return

    await interaction.response.defer()
    sonuclar = await radyo_ara(isim)
    if not sonuclar:
        await interaction.followup.send(f"**{isim}** icin radyo bulunamadi.")
        return

    radyo_istasyonu = sonuclar[0]
    stream_url = radyo_istasyonu.get("url_resolved") or radyo_istasyonu.get("url")
    radyo_adi = radyo_istasyonu.get("name", isim)
    ulke = radyo_istasyonu.get("country", "")
    favicon = radyo_istasyonu.get("favicon", "")

    if not stream_url:
        await interaction.followup.send(f"**{radyo_adi}** icin stream URL bulunamadi.")
        return

    guild = interaction.guild
    voice_channel = interaction.user.voice.channel
    player = get_player(guild.id)
    player.text_channel_id = interaction.channel.id
    player.voice_channel_id = voice_channel.id
    try:
        vc = await ensure_voice_player(guild, voice_channel)
    except Exception as exc:
        await interaction.followup.send(f"Lavalink hazir degil: {exc}")
        return

    if voice_is_playing(vc) or voice_is_paused(vc):
        await voice_stop(vc)
    async with player.lock:
        player.queue.clear()
        player.current = None
        player.starting = False
        player.skip_requested = True
        player.mode = "radio"
        if player.prefetch_task and not player.prefetch_task.done():
            player.prefetch_task.cancel()

    try:
        radio_track = Track(
            source="radio",
            query=stream_url,
            title=f"Radyo: {radyo_adi}",
            webpage_url=stream_url,
            thumbnail=favicon or None,
            resolved=True,
        )
        playable = await resolve_lavalink_track(radio_track)
        await vc.play(playable, volume=max(0, min(150, int(player.volume * 100))))
        player.current = radio_track

        embed = discord.Embed(
            title="Radyo Baslatildi",
            description=f"**{radyo_adi}**",
            color=0x9b59b6,
        )
        if ulke:
            embed.add_field(name="Ulke", value=ulke, inline=True)
        embed.add_field(name="Stream", value=f"[Baglanti]({stream_url})", inline=True)
        embed.set_footer(text="Durdurmak icin /kapat kullanabilirsin")
        if favicon:
            embed.set_thumbnail(url=favicon)

        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Radyo baslatilamadi: {e}")


@bot.tree.command(name="radyolar", description="Arama sonuçlarını listeler, birden fazla sonuç varsa seçim yapabilirsin")
@app_commands.describe(isim="Radyo adı")
async def radyolar(interaction: discord.Interaction, isim: str):
    await interaction.response.defer()
    sonuclar = await radyo_ara(isim)
    if not sonuclar:
        await interaction.followup.send(f"❌ **{isim}** için sonuç bulunamadı.")
        return

    embed = discord.Embed(title=f"📻 '{isim}' için Radyo Sonuçları", color=0x9b59b6)
    for i, r in enumerate(sonuclar[:10], 1):
        ad = r.get("name", "?")
        ulke = r.get("country", "?")
        bitrate = r.get("bitrate", "?")
        embed.add_field(
            name=f"{i}. {ad}",
            value=f"🌍 {ulke} • 🎚️ {bitrate} kbps",
            inline=False
        )
    embed.set_footer(text="İstediğin radyoyu çalmak için /radyo [tam isim] kullan")
    await interaction.followup.send(embed=embed)

# ─────────────────────────────────────────────────────────────────────────────
bot.run(DISCORD_TOKEN)
