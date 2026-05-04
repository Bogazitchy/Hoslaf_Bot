# 🎵 Hoşlaf Bot

Hoşlaf Discord sunucusu için geliştirilmiş çok amaçlı bot. Müzik çalma, futbol takibi, güncel haberler, web araması ve tarihte bugün özelliklerini tek çatı altında toplar.

---

## ✨ Özellikler

- 🎵 **Müzik** — YouTube, Spotify ve SoundCloud desteği, kuyruk sistemi
- ⚽ **Futbol** — Canlı skorlar, maç takvimi, puan durumu, turnuva ağacı
- 📰 **Haberler** — Türkiye gündemi, her akşam 18:00'de otomatik paylaşım
- 🔍 **Web Araması** — Exa AI destekli anlık arama
- 📅 **Tarihte Bugün** — Wikipedia tabanlı günlük tarih olayları

---

## ⚙️ Kurulum

### Gereksinimler

- Python 3.10+
- ffmpeg
- pip

### 1. Repoyu klonla

```bash
git clone https://github.com/Bogazitchy/Hoslaf_Bot.git
cd Hoslaf_Bot
```

### 2. Kütüphaneleri kur

```bash
pip install discord.py[voice] yt-dlp spotipy lyricsgenius aiohttp pytz python-dotenv PyNaCl davey
```

### 3. `.env` dosyası oluştur

Klasörün içine `.env` adında bir dosya oluştur ve şu bilgileri doldur:

```env
DISCORD_TOKEN=your_discord_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
GENIUS_TOKEN=your_genius_token
EXA_API_KEY=your_exa_api_key
APIF_KEY=your_api_football_key
FD_KEY=your_football_data_key
```

### 4. Kanal ID'lerini ayarla

`bot.py` içindeki şu sabitleri kendi kanallarınla değiştir:

```python
HABER_KANAL_ID  = ...  # Türkiye haberleri kanalı
FUTBOL_KANAL_ID = ...  # Futbol maç takvimi kanalı
WIKI_KANAL_ID   = ...  # Tarihte bugün kanalı
```

### 5. Botu başlat

```bash
python bot.py
```

---

### Systemd Servisi Olarak Çalıştırma (Linux)

`/etc/systemd/system/hoslafbot.service` dosyası oluştur:

```ini
[Unit]
Description=Hoşlaf Bot
After=network.target

[Service]
Type=simple
User=kullanici_adi
WorkingDirectory=/path/to/Hoslaf_Bot
ExecStart=/usr/bin/python bot.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hoslafbot.service
sudo systemctl start hoslafbot.service
```

---

## 🎵 Müzik Komutları

| Komut | Açıklama |
|-------|----------|
| `/oynat [şarkı]` | Şarkı adı, YouTube, Spotify veya SoundCloud linki ile şarkı çalar. Playlist desteği vardır. |
| `/kapat` | Şarkıyı durdurur ve ses kanalından ayrılır. |
| `/atla [miktar]` | Şu an çalan şarkıyı atlar. Miktar belirtilirse o kadar şarkı atlanır. |
| `/duraklat` | Şarkıyı duraklatır. |
| `/devam` | Duraklatılan şarkıyı devam ettirir. |
| `/sardır [saniye]` | Şarkıyı belirtilen saniyeye sarar. |
| `/karistir` | Kuyruktaki şarkıları karıştırır. |
| `/ses [0-100]` | Ses seviyesini ayarlar. |
| `/kuyruk` | Şu an çalan şarkıyı ve sıradaki şarkıları gösterir. |
| `/lyrics` | Şu an çalan şarkının sözlerini gösterir. |

### Desteklenen Kaynaklar
- ✅ YouTube (link veya arama)
- ✅ YouTube Playlist
- ✅ Spotify (tek şarkı)
- ✅ Spotify Playlist & Album
- ✅ SoundCloud

---

## ⚽ Futbol Komutları

| Komut | Açıklama |
|-------|----------|
| `/bugun` | Bugün oynanan tüm maçları gösterir. |
| `/canli` | Şu an oynanan maçların canlı skorlarını gösterir. |
| `/lig [lig]` | Seçilen ligin bugünkü maçlarını gösterir. |
| `/puandurumu [lig]` | Seçilen ligin puan durumunu gösterir. |
| `/turnuva` | Şampiyonlar Ligi turnuva ağacını gösterir. |

### Desteklenen Ligler
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
- 🇪🇸 La Liga
- 🇩🇪 Bundesliga
- 🇮🇹 Serie A
- 🇫🇷 Ligue 1
- ⭐ Şampiyonlar Ligi

### Otomatik Gönderim
Her gün gece **00:01 TR** saatinde futbol kanalına günün maç takvimi otomatik olarak gönderilir.

---

## 📰 Haber Komutları

| Komut | Açıklama |
|-------|----------|
| `/haber` | Türkiye gündeminden anlık 10 haber getirir. |

Her gün saat **18:00 TR** saatinde haber kanalına Türkiye gündemi otomatik olarak gönderilir.

---

## 🔍 Arama Komutu

| Komut | Açıklama |
|-------|----------|
| `/ara [sorgu]` | Exa AI ile web'de arama yapar, sonuçları embed olarak gösterir. |

---

## 📅 Tarihte Bugün Komutları

| Komut | Açıklama |
|-------|----------|
| `/tarihtebugun` | Bugün tarihte yaşanan olayları Wikipedia'dan getirir. |
| `/tarihsorgu [ay] [gün]` | Belirtilen tarihteki olayları gösterir. |
| `/rastgeletarih` | Rastgele bir tarihteki olayları gösterir. |

Her gün saat **12:00 TR** saatinde tarihte bugün kanalına otomatik gönderim yapılır.

---

## 🔑 API Anahtarları

| Servis | Nereden Alınır |
|--------|---------------|
| Discord Bot Token | [discord.com/developers](https://discord.com/developers/applications) |
| Spotify Client ID/Secret | [developer.spotify.com](https://developer.spotify.com/dashboard) |
| Genius Token | [genius.com/api-clients](https://genius.com/api-clients) |
| Exa API Key | [dashboard.exa.ai](https://dashboard.exa.ai) |
| API-Football Key | [api-sports.io](https://api-sports.io) |
| Football-Data Key | [football-data.org](https://www.football-data.org) |

---

## 📁 Dosya Yapısı

```
Hoslaf_Bot/
├── bot.py          # Ana bot dosyası
├── .env            # API anahtarları (git'e yükleme!)
├── .gitignore
└── README.md
```

---

## 👤 Geliştirici

**Bogazitchy** — [github.com/Bogazitchy](https://github.com/Bogazitchy)
