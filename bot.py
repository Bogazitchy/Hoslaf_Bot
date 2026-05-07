import discord
from discord import app_commands
from discord.ext import tasks, commands
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio
import os
import random
import lyricsgenius
import aiohttp
import datetime
from datetime import date
import pytz
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

# ── Tokenlar & Ayarlar ────────────────────────────────────────────────────────
DISCORD_TOKEN  = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_TOKEN   = os.getenv("GENIUS_TOKEN")
EXA_API_KEY    = os.getenv("EXA_API_KEY")
APIF_KEY       = os.getenv("APIF_KEY")
FD_KEY         = os.getenv("FD_KEY")

HABER_KANAL_ID   = 
FUTBOL_KANAL_ID  = 
WIKI_KANAL_ID    = 
HABER_SAATI      = datetime.time(hour=15, minute=0)   # UTC 15:00 = TR 18:00
WIKI_SAATI       = datetime.time(hour=9, minute=0)    # UTC 09:00 = TR 12:00
WIKI_OLAY_SAYISI = 5
TURKEY_TZ        = pytz.timezone("Europe/Istanbul")

APIF_HOST = "v3.football.api-sports.io"
APIF_URL  = f"https://{APIF_HOST}"
FD_URL    = "https://api.football-data.org/v4"

# ── Spotify & Genius ──────────────────────────────────────────────────────────
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT,
    client_secret=SPOTIFY_SECRET
))
genius = lyricsgenius.Genius(GENIUS_TOKEN, timeout=10, retries=2)

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
executor = ThreadPoolExecutor(max_workers=4)

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
        gunluk_haber.start()
        daily_schedule_task.start()
        gunluk_wiki.start()
        print("Slash komutları senkronize edildi.")

bot = HoslafBot()

queues: dict[int, list] = {}
text_channels: dict[int, discord.TextChannel] = {}
current_track: dict[int, str] = {}

# ─────────────────────────────────────────────────────────────────────────────
#  MÜZİK YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]

def is_spotify_url(t): return "spotify.com" in t
def is_url(t): return t.startswith("http://") or t.startswith("https://")
def is_playlist_url(t): return ("list=" in t) or ("spotify.com/playlist" in t) or ("spotify.com/album" in t)

def _spotify_to_search_query(url):
    track_id = url.split("/track/")[-1].split("?")[0]
    track = sp.track(track_id)
    artists = ", ".join(a["name"] for a in track["artists"])
    return f"{artists} - {track['name']}"

def _spotify_playlist_to_queries(url):
    import requests
    queries = []
    token_resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT, SPOTIFY_SECRET)
    )
    token = token_resp.json().get("access_token")
    if "spotify.com/playlist" in url:
        playlist_id = url.split("/playlist/")[-1].split("?")[0]
        offset = 0
        while True:
            r = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                headers={"Authorization": f"Bearer {token}"},
                params={"limit": 100, "offset": offset}
            )
            data = r.json()
            if r.status_code != 200:
                break
            for item in data.get("items", []):
                track = item.get("track")
                if track and track.get("name"):
                    artists = ", ".join(a["name"] for a in track["artists"])
                    queries.append(f"{artists} - {track['name']}")
            if not data.get("next"):
                break
            offset += 100
    elif "spotify.com/album" in url:
        album_id = url.split("/album/")[-1].split("?")[0]
        r = requests.get(
            f"https://api.spotify.com/v1/albums/{album_id}/tracks",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 50}
        )
        for track in r.json().get("items", []):
            if track.get("name"):
                artists = ", ".join(a["name"] for a in track["artists"])
                queries.append(f"{artists} - {track['name']}")
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
        return info["url"], info.get("title", "Bilinmeyen Şarkı")

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

async def fetch_audio(query):
    return await asyncio.get_event_loop().run_in_executor(executor, _fetch_audio, query)

async def fetch_playlist_yt(url):
    return await asyncio.get_event_loop().run_in_executor(executor, _fetch_playlist_yt, url)

async def spotify_to_search_query(url):
    return await asyncio.get_event_loop().run_in_executor(executor, _spotify_to_search_query, url)

async def spotify_playlist_to_queries(url):
    return await asyncio.get_event_loop().run_in_executor(executor, _spotify_playlist_to_queries, url)

async def play_next(guild):
    queue = get_queue(guild.id)
    vc = guild.voice_client
    if not queue or not vc:
        current_track.pop(guild.id, None)
        return
    item = queue.pop(0)
    try:
        if item[0] == "__search__":
            audio_url, title = await fetch_audio(f"ytsearch:{item[1]}")
        elif item[0].startswith("https://www.youtube.com/watch"):
            audio_url, title = await fetch_audio(item[0])
        else:
            audio_url, title = item[0], item[1]
    except Exception as e:
        print(f"Şarkı yüklenemedi: {e}")
        await play_next(guild)
        return
    current_track[guild.id] = title
    def after_play(error):
        if error: print(f"Oynatma hatası: {error}")
        asyncio.run_coroutine_threadsafe(play_next(guild), bot.loop)
    vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTS), after=after_play)
    vc.source = discord.PCMVolumeTransformer(vc.source, volume=0.8)
    channel = text_channels.get(guild.id)
    if channel:
        await channel.send(f"🎵 Şimdi çalıyor: **{title}**")

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
    print(f"✅ Hoşlaf Bot hazır! {bot.user}")

# ─────────────────────────────────────────────────────────────────────────────
#  MÜZİK KOMUTLARI
# ─────────────────────────────────────────────────────────────────────────────

@bot.tree.command(name="oynat", description="Şarkı adı, YouTube/Spotify/SoundCloud linki veya playlist çal")
@app_commands.describe(sarki="Şarkı adı, YouTube linki, Spotify linki veya playlist linki")
async def oynat(interaction: discord.Interaction, sarki: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Bir ses kanalında olman gerekiyor!", ephemeral=True)
        return
    voice_channel = interaction.user.voice.channel
    guild = interaction.guild
    await interaction.response.defer()
    text_channels[guild.id] = interaction.channel
    vc = guild.voice_client
    if vc is None:
        vc = await voice_channel.connect()
    elif vc.channel != voice_channel:
        await vc.move_to(voice_channel)
    queue = get_queue(guild.id)
    try:
        if "spotify.com/playlist" in sarki or "spotify.com/album" in sarki:
            queries = await spotify_playlist_to_queries(sarki)
            if not queries:
                await interaction.followup.send("❌ Playlist boş veya bulunamadı.")
                return
            first_url, first_title = await fetch_audio(f"ytsearch:{queries[0]}")
            for q in queries[1:]:
                queue.append(("__search__", q))
            if vc.is_playing() or vc.is_paused():
                queue.insert(0, (first_url, first_title))
                await interaction.followup.send(f"📋 **{len(queries)} şarkı** kuyruğa eklendi!")
            else:
                queue.insert(0, (first_url, first_title))
                await interaction.followup.send(f"▶️ **{len(queries)} şarkılık Spotify playlist** başlıyor!")
                await play_next(guild)
        elif is_spotify_url(sarki):
            query = await spotify_to_search_query(sarki)
            audio_url, title = await fetch_audio(f"ytsearch:{query}")
            if vc.is_playing() or vc.is_paused():
                queue.append((audio_url, title))
                await interaction.followup.send(f"📋 **{title}** kuyruğa eklendi! (Pozisyon: {len(queue)})")
            else:
                queue.insert(0, (audio_url, title))
                await interaction.followup.send(f"▶️ Başlıyor: **{title}**")
                await play_next(guild)
        elif is_url(sarki) and is_playlist_url(sarki):
            tracks = await fetch_playlist_yt(sarki)
            if not tracks:
                await interaction.followup.send("❌ Playlist boş veya bulunamadı.")
                return
            first_url, first_title = await fetch_audio(tracks[0][0])
            for video_url, title in tracks[1:]:
                queue.append((video_url, title))
            if vc.is_playing() or vc.is_paused():
                queue.insert(0, (first_url, first_title))
                await interaction.followup.send(f"📋 **{len(tracks)} şarkı** kuyruğa eklendi!")
            else:
                queue.insert(0, (first_url, first_title))
                await interaction.followup.send(f"▶️ **{len(tracks)} şarkılık YouTube playlist** başlıyor!")
                await play_next(guild)
        elif is_url(sarki):
            audio_url, title = await fetch_audio(sarki)
            if vc.is_playing() or vc.is_paused():
                queue.append((audio_url, title))
                await interaction.followup.send(f"📋 **{title}** kuyruğa eklendi! (Pozisyon: {len(queue)})")
            else:
                queue.insert(0, (audio_url, title))
                await interaction.followup.send(f"▶️ Başlıyor: **{title}**")
                await play_next(guild)
        else:
            audio_url, title = await fetch_audio(f"ytsearch:{sarki}")
            if vc.is_playing() or vc.is_paused():
                queue.append((audio_url, title))
                await interaction.followup.send(f"📋 **{title}** kuyruğa eklendi! (Pozisyon: {len(queue)})")
            else:
                queue.insert(0, (audio_url, title))
                await interaction.followup.send(f"▶️ Başlıyor: **{title}**")
                await play_next(guild)
    except Exception as e:
        await interaction.followup.send(f"❌ Hata: {e}")

@bot.tree.command(name="kapat", description="Şarkıyı kapatır ve ses kanalından ayrılır")
async def kapat(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        queues[interaction.guild.id] = []
        current_track.pop(interaction.guild.id, None)
        await vc.disconnect()
        await interaction.response.send_message("⏹️ Kapatıldı!")
    else:
        await interaction.response.send_message("❌ Zaten bir ses kanalında değilim.", ephemeral=True)

@bot.tree.command(name="atla", description="Şarkıyı atlar")
@app_commands.describe(miktar="Kaç şarkı atlanacak (varsayılan 1)")
async def atla(interaction: discord.Interaction, miktar: int = 1):
    vc = interaction.guild.voice_client
    if not vc or (not vc.is_playing() and not vc.is_paused()):
        await interaction.response.send_message("❌ Şu an çalan bir şarkı yok.", ephemeral=True)
        return
    queue = get_queue(interaction.guild.id)
    del queue[:min(miktar - 1, len(queue))]
    vc.stop()
    await interaction.response.send_message(f"⏭️ **{miktar}** şarkı atlandı!" if miktar > 1 else "⏭️ Atlandı!")

@bot.tree.command(name="duraklat", description="Şarkıyı duraklatır")
async def duraklat(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Duraklatıldı!")
    else:
        await interaction.response.send_message("❌ Şu an çalan bir şarkı yok.", ephemeral=True)

@bot.tree.command(name="devam", description="Duraklatılan şarkıyı devam ettirir")
async def devam(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Devam ediliyor!")
    else:
        await interaction.response.send_message("❌ Duraklatılmış bir şarkı yok.", ephemeral=True)

@bot.tree.command(name="sardır", description="Şarkıyı belirtilen saniyeye sarar")
@app_commands.describe(saniye="Kaçıncı saniyeye sarılacak")
async def sardir(interaction: discord.Interaction, saniye: int):
    vc = interaction.guild.voice_client
    if not vc or (not vc.is_playing() and not vc.is_paused()):
        await interaction.response.send_message("❌ Şu an çalan bir şarkı yok.", ephemeral=True)
        return
    guild = interaction.guild
    title = current_track.get(guild.id, "")
    await interaction.response.defer()
    try:
        if not title:
            await interaction.followup.send("❌ Şarkı bilgisi bulunamadı.")
            return
        audio_url, _ = await fetch_audio(f"ytsearch:{title}")
        seek_opts = {"before_options": f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {saniye}", "options": "-vn"}
        volume = 0.8
        if vc.source and hasattr(vc.source, "volume"):
            volume = vc.source.volume
        def after_seek(error):
            if error: print(f"Seek hatası: {error}")
            asyncio.run_coroutine_threadsafe(play_next(guild), bot.loop)
        vc.stop()
        await asyncio.sleep(0.5)
        vc.play(discord.FFmpegPCMAudio(audio_url, **seek_opts), after=after_seek)
        vc.source = discord.PCMVolumeTransformer(vc.source, volume=volume)
        dakika, sn = divmod(saniye, 60)
        await interaction.followup.send(f"⏩ **{dakika:02d}:{sn:02d}** saniyesine sarıldı!")
    except Exception as e:
        await interaction.followup.send(f"❌ Hata: {e}")

@bot.tree.command(name="karistir", description="Oynatma listesini karıştırır")
async def karistir(interaction: discord.Interaction):
    queue = get_queue(interaction.guild.id)
    if not queue:
        await interaction.response.send_message("📋 Kuyruk zaten boş.", ephemeral=True)
        return
    random.shuffle(queue)
    await interaction.response.send_message(f"🔀 **{len(queue)} şarkı** karıştırıldı!")

@bot.tree.command(name="ses", description="Ses seviyesini ayarla (0-100)")
@app_commands.describe(seviye="Ses seviyesi (0-100)")
async def ses(interaction: discord.Interaction, seviye: int):
    vc = interaction.guild.voice_client
    if vc and vc.source:
        vc.source.volume = max(0, min(seviye, 100)) / 100
        await interaction.response.send_message(f"🔊 Ses seviyesi: **{seviye}%**")
    else:
        await interaction.response.send_message("❌ Şu an çalan bir şarkı yok.", ephemeral=True)

@bot.tree.command(name="kuyruk", description="Kuyruğu göster")
async def kuyruk_cmd(interaction: discord.Interaction):
    queue = get_queue(interaction.guild.id)
    title = current_track.get(interaction.guild.id)
    lines = []
    if title: lines.append(f"▶️ **Şimdi çalıyor:** {title}")
    if not queue:
        await interaction.response.send_message("\n".join(lines) if lines else "📋 Kuyruk boş.")
        return
    lines.append("📋 **Sıradaki şarkılar:**")
    for i, item in enumerate(queue[:20]):
        lines.append(f"{i+1}. {item[1]}")
    if len(queue) > 20:
        lines.append(f"... ve {len(queue)-20} şarkı daha")
    await interaction.response.send_message("\n".join(lines))

@bot.tree.command(name="lyrics", description="Şu an çalan şarkının sözlerini gösterir")
async def lyrics(interaction: discord.Interaction):
    title = current_track.get(interaction.guild.id)
    if not title:
        await interaction.response.send_message("❌ Şu an çalan bir şarkı yok.", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        loop = asyncio.get_event_loop()
        song = await loop.run_in_executor(executor, lambda: genius.search_song(title))
        if not song:
            await interaction.followup.send(f"❌ **{title}** için şarkı sözü bulunamadı.")
            return
        lyrics_text = song.lyrics
        if "EmbedShare" in lyrics_text:
            lyrics_text = lyrics_text[:lyrics_text.rfind("EmbedShare")]
        header = f"🎤 **{song.title}** — {song.artist}\n\n"
        max_len = 1990 - len(header)
        if len(lyrics_text) <= max_len:
            await interaction.followup.send(header + lyrics_text)
        else:
            await interaction.followup.send(header + lyrics_text[:max_len] + "…")
            remaining = lyrics_text[max_len:]
            while remaining:
                chunk = remaining[:1990]
                remaining = remaining[1990:]
                await interaction.channel.send(chunk + ("…" if remaining else ""))
    except Exception as e:
        await interaction.followup.send(f"❌ Şarkı sözleri alınamadı: {e}")

# ─────────────────────────────────────────────────────────────────────────────
#  HABER & ARAMA KOMUTLARI
# ─────────────────────────────────────────────────────────────────────────────

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


@bot.tree.command(name="radyo", description="Radyo yayını başlatır. Radyo adı yazarak arayabilirsin.")
@app_commands.describe(isim="Radyo adı (örn: Kral FM, TRT Radyo 1, Power FM)")
async def radyo(interaction: discord.Interaction, isim: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Bir ses kanalında olman gerekiyor!", ephemeral=True)
        return

    await interaction.response.defer()

    # Radyoyu ara
    sonuclar = await radyo_ara(isim)
    if not sonuclar:
        await interaction.followup.send(f"❌ **{isim}** için radyo bulunamadı.")
        return

    # En iyi sonucu seç (clickcount'a göre sıralı geliyor)
    radyo_istasyonu = sonuclar[0]
    stream_url = radyo_istasyonu.get("url_resolved") or radyo_istasyonu.get("url")
    radyo_adi = radyo_istasyonu.get("name", isim)
    ulke = radyo_istasyonu.get("country", "")
    favicon = radyo_istasyonu.get("favicon", "")

    if not stream_url:
        await interaction.followup.send(f"❌ **{radyo_adi}** için stream URL bulunamadı.")
        return

    guild = interaction.guild
    voice_channel = interaction.user.voice.channel
    vc = guild.voice_client

    # Ses kanalına bağlan
    if vc is None:
        vc = await voice_channel.connect()
    elif vc.channel != voice_channel:
        await vc.move_to(voice_channel)

    # Çalıyorsa durdur
    if vc.is_playing() or vc.is_paused():
        vc.stop()
        queues[guild.id] = []

    # Radyoyu çal
    try:
        vc.play(discord.FFmpegPCMAudio(stream_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn"))
        vc.source = discord.PCMVolumeTransformer(vc.source, volume=0.8)
        current_track[guild.id] = f"📻 {radyo_adi}"

        embed = discord.Embed(
            title="📻 Radyo Başlatıldı",
            description=f"**{radyo_adi}**",
            color=0x9b59b6
        )
        if ulke:
            embed.add_field(name="🌍 Ülke", value=ulke, inline=True)
        embed.add_field(name="🔗 Stream", value=f"[Bağlantı]({stream_url})", inline=True)
        embed.set_footer(text="Durdurmak için /kapat kullanabilirsin")
        if favicon:
            embed.set_thumbnail(url=favicon)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Radyo başlatılamadı: {e}")


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
