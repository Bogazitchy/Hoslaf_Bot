<div align="center">

<img src="./assets/hoslaf-banner.png" alt="Hoslaf Bot banner" width="100%">

<br>

# HOSLAF BOT

### Discord sunuculari icin modern muzik, radyo, futbol, haber ve bilgi asistani

<p>
  <strong>Kalici muzik paneli</strong>, <strong>playlist destegi</strong>,
  <strong>kuyruk yonetimi</strong>, <strong>otomatik oneriler</strong> ve
  <strong>canli bilgi komutlari</strong> tek botta.
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="discord.py">
  <img src="https://img.shields.io/badge/Audio-Lavalink%20%2B%20Wavelink-00A86B?style=for-the-badge&logo=waves&logoColor=white" alt="Lavalink + Wavelink">
  <img src="https://img.shields.io/badge/Spotify-Ready-1DB954?style=for-the-badge&logo=spotify&logoColor=white" alt="Spotify">
  <img src="https://img.shields.io/badge/VPS-24%2F7-111111?style=for-the-badge&logo=linux&logoColor=white" alt="VPS">
</p>

<p>
  <a href="#-one-cikanlar">One Cikanlar</a> •
  <a href="#-muzik-paneli">Muzik Paneli</a> •
  <a href="#-komutlar">Komutlar</a> •
  <a href="#-kurulum">Kurulum</a> •
  <a href="#-guvenlik">Guvenlik</a>
</p>

</div>

---

## Genel Bakis

Hoslaf Bot, Discord sunucularinda muzik dinlemeyi temiz, hizli ve kontrol
edilebilir hale getirmek icin gelistirilmis cok amacli bir bottur. Muzik
tarafinda YouTube, Spotify, SoundCloud ve radyo kaynaklarini destekler; bunun
yaninda futbol, haber, web arama ve tarih komutlariyla sunucu ici gunluk
ihtiyaclari tek noktada toplar.

Botun en guclu tarafi kalici muzik panelidir. Her komutta yeni panel spam'i
olusturmak yerine ayni panel guncellenir; gecici bilgilendirme mesajlari ise
otomatik temizlenir. Boylece muzik kanali duzenli kalir.

<div align="center">
  <img src="./assets/hoslaf-logo.png" alt="Hoslaf Bot logo" width="360">
</div>

## One Cikanlar

<table>
  <tr>
    <td width="50%">
      <h3>Modern Muzik Paneli</h3>
      Tek mesaj uzerinden calan sarki, ilerleme cubugu, ses seviyesi, isteyen
      kisi, tekrar modu, altyapi durumu ve kuyruk ozeti gorulur.
    </td>
    <td width="50%">
      <h3>Dropdown Kontroller</h3>
      Panel icinden kuyruktan sarki secilebilir, sarki kaldirilabilir, tekrar
      modu degistirilebilir ve kayitli playlist baslatilabilir.
    </td>
  </tr>
  <tr>
    <td>
      <h3>Playlist Sistemi</h3>
      Sunucuya ozel muzik listeleri kaydedilebilir, listelenebilir, silinebilir
      ve panel uzerinden tekrar baslatilabilir.
    </td>
    <td>
      <h3>Tekrar Modlari</h3>
      Kapali, sarki tekrari ve kuyruk tekrari desteklenir. Panelde anlik mod
      acik sekilde gosterilir.
    </td>
  </tr>
  <tr>
    <td>
      <h3>Metadata Cache</h3>
      Sik aranan sarkilarin baslik, sure, thumbnail ve kaynak bilgileri cache'e
      alinir. Tekrar eden komutlarda cozumleme daha hizli olur.
    </td>
    <td>
      <h3>Reconnect Resume</h3>
      Bot ses kanalindan dustugunde calan sarkiyi yaklasik kaldigi pozisyona
      gore tekrar siraya alarak toparlanmayi kolaylastirir.
    </td>
  </tr>
  <tr>
    <td>
      <h3>Radyo ve Guncel Bilgi</h3>
      Internet radyolari, canli maclar, lig puan durumlari, haberler, web arama
      ve tarihte bugun komutlari bulunur.
    </td>
    <td>
      <h3>24/7 Calisma</h3>
      Linux VPS systemd servisi ve Windows servis yardimcilariyla surekli
      calisma senaryosuna uygundur.
    </td>
  </tr>
</table>

## Muzik Paneli

Panel, muzik kanalini temiz tutmak icin ayni mesaj uzerinde guncellenir.
Butonlar ve secim menuleri tek panelde toplanir.

```text
Simdi caliyor: Batuflex & Era7capone - Gasolina

Ilerleme
01:24 =======o----------- 03:45

Ses: %80
Isteyen: melihwastaken
Tekrar: Kuyruk
Altyapi: Lavalink
```

### Panel Kontrolleri

| Kontrol | Islev |
| --- | --- |
| Duraklat / Devam | Oynatmayi duraklatir veya kaldigi yerden surdurur. |
| Atla | Calan parcayi gecip siradaki parcaya devam eder. |
| Durdur | Aktif oynatmayi ve kuyrugu temizler. |
| Kuyruk | Kuyrugun detayli gorunumunu acar. |
| Ses - / Ses + | Ses seviyesini panelden degistirir. |
| Kuyruktan sarki sec | Bekleyen sarkilardan birini one alir ve calar. |
| Sarkiyi kuyruktan kaldir | Secilen parcayi kuyruktan siler. |
| Tekrar modu sec | Kapali, sarki veya kuyruk tekrari arasinda gecis yapar. |
| Playlist baslat | Sunucuya kayitli playlistlerden birini baslatir. |

## Muzik Ozellikleri

- Lavalink v4 ses altyapisi
- Wavelink tabanli Discord player
- YouTube video ve playlist destegi
- Spotify sarki, album ve playlist cozumleme
- SoundCloud link destegi
- Radio Browser ile internet radyosu arama
- Kuyruk on yukleme
- Kuyruk karistirma
- Sarki gecmisi
- Sarki sozu arama
- Otomatik oneriler
- Kullanici muzik profili
- Sunucuya ozel playlist kayitlari
- Metadata cache
- Ses kanali kopmalarinda toparlanma
- Java/Lavalink servis mimarisiyle daha stabil oynatma

## Komutlar

### Muzik

| Komut | Aciklama |
| --- | --- |
| `/oynat sarki` | Sarki adi, YouTube/Spotify/SoundCloud linki veya playlist calar. |
| `/kapat` | Muzigi kapatir, kuyrugu temizler ve ses kanalindan ayrilir. |
| `/atla miktar` | Calan parcayi veya belirtilen sayida parcayi atlar. |
| `/duraklat` | Aktif parcayi duraklatir. |
| `/devam` | Duraklatilan parcayi devam ettirir. |
| `/sardir saniye` | Parcayi belirtilen saniyeye sarar. |
| `/karistir` | Kuyrugu karistirir. |
| `/ses seviye` | Ses seviyesini 0-100 arasinda ayarlar. |
| `/kuyruk` | Calan parca ve siradaki parcalari gosterir. |
| `/gecmis` | Son calinan sarkilari listeler. |
| `/otomatik ac/kapat` | Kuyruk bittiginde otomatik oneriyi acar veya kapatir. |
| `/tekrar mod` | Kapali, sarki veya kuyruk tekrar modunu secer. |
| `/playlistkaydet ad` | Mevcut calan sarki ve kuyrugu playlist olarak kaydeder. |
| `/playlistler` | Sunucudaki kayitli playlistleri listeler. |
| `/playlistsil ad` | Kayitli playlisti siler. |
| `/muzikprofil` | Kullanici muzik istatistiklerini gosterir. |
| `/lyrics` | Calan sarkinin sozlerini getirir. |

### Radyo

| Komut | Aciklama |
| --- | --- |
| `/radyo isim` | Radyo arar ve en uygun sonucu oynatir. |
| `/radyolar isim` | Birden fazla radyo sonucunu secim listesiyle gosterir. |

### Futbol

| Komut | Aciklama |
| --- | --- |
| `/bugun` | Bugunun mac takvimini gosterir. |
| `/canli` | Devam eden karsilasmalarin skorlarini gosterir. |
| `/lig lig` | Secilen ligin bugunku maclarini listeler. |
| `/puandurumu lig` | Secilen ligin puan durumunu gosterir. |
| `/turnuva` | Sampiyonlar Ligi turnuva agacini gosterir. |

### Haber, Arama ve Tarih

| Komut | Aciklama |
| --- | --- |
| `/haber` | Turkiye gundeminden haberleri getirir. |
| `/ara sorgu` | Exa AI ile web aramasi yapar. |
| `/tarihtebugun` | Bugunun tarihsel olaylarini gosterir. |
| `/tarihsorgu ay gun` | Belirli bir tarihte yasanan olaylari getirir. |
| `/rastgeletarih` | Rastgele bir gunun tarihsel olaylarini gosterir. |

## Kurulum

### Gereksinimler

- Python 3.10 veya uzeri
- Java 17 veya uzeri
- Lavalink v4
- Discord bot tokeni
- Spotify API bilgileri
- Genius API tokeni
- Exa API anahtari
- Futbol verileri icin API-Football ve Football-Data anahtarlari

### Depoyu Klonla

```bash
git clone https://github.com/Bogazitchy/Hoslaf_Bot.git
cd Hoslaf_Bot
```

### Sanal Ortami Kur

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Linux:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

### Java Kontrolu

```bash
java -version
```

Lavalink icin Java 17 veya uzeri gerekir. VPS ortaminda Java 21 onerilir.

### Lavalink Node

Botun muzik oynatma motoru Lavalink uzerinden calisir. Lavalink, Python bot
surecinden ayri bir Java servisi olarak ayakta durur ve Discord ses aktarimini
yonetir.

Canli VPS yapisi:

```text
/opt/lavalink/
├── Lavalink.jar
├── application.yml
└── logs/
```

Systemd servis kontrolu:

```bash
systemctl status lavalink.service
journalctl -u lavalink.service -n 100 --no-pager
```

Lavalink yalnizca `127.0.0.1:2333` uzerinden dinler. Dis dunyaya acik
degildir; bot ayni VPS icinden baglanir.

### Ortam Degiskenleri

Proje kokunde `.env` dosyasi olustur:

```env
DISCORD_TOKEN=discord_bot_token

SPOTIFY_CLIENT_ID=spotify_client_id
SPOTIFY_CLIENT_SECRET=spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

GENIUS_TOKEN=genius_token
EXA_API_KEY=exa_api_key
APIF_KEY=api_football_key
FD_KEY=football_data_key

LAVALINK_HOST=127.0.0.1
LAVALINK_PORT=2333
LAVALINK_URI=http://127.0.0.1:2333
LAVALINK_PASSWORD=youshallnotpass
```

| Degisken | Kullanim |
| --- | --- |
| `DISCORD_TOKEN` | Discord bot kimlik dogrulamasi |
| `SPOTIFY_CLIENT_ID` | Spotify katalog erisimi |
| `SPOTIFY_CLIENT_SECRET` | Spotify uygulama dogrulamasi |
| `SPOTIFY_REDIRECT_URI` | Spotify yetkilendirme donus adresi |
| `GENIUS_TOKEN` | Sarki sozu aramasi |
| `EXA_API_KEY` | Web arama ozelligi |
| `APIF_KEY` | API-Football verileri |
| `FD_KEY` | Football-Data verileri |
| `LAVALINK_*` | Lavalink node baglantisi |

### Botu Baslat

Windows:

```powershell
.\.venv\Scripts\python.exe bot.py
```

Linux:

```bash
./.venv/bin/python bot.py
```

## Spotify Playlist Yetkilendirmesi

Bazi Spotify playlistleri kullanici yetkilendirmesi gerektirir.

1. Spotify Developer Dashboard icinde Redirect URI olarak
   `http://127.0.0.1:8888/callback` adresini ekle.
2. Yetkilendirme aracini calistir:

```powershell
.\.venv\Scripts\python.exe spotify_authorize.py
```

3. Terminalde verilen baglantiyi tarayicida ac.
4. Spotify izin ekranini onayla.
5. Yonlendirildigin tam adresi terminale yapistir.

Basarili islem sonunda `.spotify_user_cache` olusur. Bu dosya repoya
yuklenmemelidir.

## Servis Olarak Calistirma

### Linux VPS

Ornek systemd servis yapisi:

```ini
[Unit]
Description=Hoslaf Discord Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=hoslafbot
Group=hoslafbot
WorkingDirectory=/opt/hoslafbot
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/hoslafbot/.venv/bin/python /opt/hoslafbot/bot.py
Restart=always
RestartSec=10
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/opt/hoslafbot

[Install]
WantedBy=multi-user.target
```

Kontrol:

```bash
systemctl status hoslafbot.service
journalctl -u hoslafbot.service -n 100 --no-pager
```

### Windows

Depoda WinSW tabanli servis yardimcilari bulunur.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install_hoslafbot_service.ps1
.\register_hoslafbot_startup_task.ps1
```

Guncelleme sonrasi kontrol:

```powershell
sc.exe query HoslafBot
```

## Proje Yapisi

```text
Hoslaf_Bot/
├── assets/
│   ├── hoslaf-banner.png
│   └── hoslaf-logo.png
├── bot.py
├── spotify_authorize.py
├── requirements.txt
├── HoslafBotService.xml
├── install_hoslafbot_service.ps1
├── run_hoslafbot_service.ps1
├── ensure_hoslafbot_service.ps1
├── register_hoslafbot_startup_task.ps1
├── register_hoslafbot_user_logon_task.ps1
├── privacy.html
├── terms.html
└── README.md
```

## Calisma Zamani Dosyalari

Bu dosyalar calisma sirasinda olusur ve repoya yuklenmez:

```text
.env
.spotify_user_cache
.spotify_client_cache
music_stats.json
music_metadata_cache.json
music_playlists.json
logs/
```

## Guvenlik

- `.env` dosyasini ve Discord tokenini asla repoya yukleme.
- Token aciga cikarsa Discord Developer Portal uzerinden hemen yenile.
- Spotify cache dosyalarini paylasma.
- `music_stats.json`, `music_metadata_cache.json` ve `music_playlists.json`
  sunucuya ait kullanim verileri icerebilir.
- Log dosyalarini paylasmadan once token, kullanici ve sunucu bilgilerini
  kontrol et.
- Bot davet linkinde yalnizca gerekli izinleri ver.

## Kullanilan Teknolojiler

<p>
  <img src="https://skillicons.dev/icons?i=python,discord,git,github,powershell,linux" alt="Kullanilan teknolojiler">
</p>

- `discord.py`: Slash komutlar, butonlar, dropdownlar ve ses baglantisi
- `Lavalink`: Ayrik ses node'u ve Discord ses aktarimi
- `Wavelink`: Python bot ile Lavalink arasindaki player katmani
- `yt-dlp`: Playlist ve metadata cozumleme yardimcilari
- `Spotipy`: Spotify icerik cozumleme
- `aiohttp` ve `requests`: Harici API istekleri
- `Genius`: Sarki sozleri
- `Exa AI`: Web aramasi
- `API-Football` ve `Football-Data`: Futbol verileri
- `systemd` ve `WinSW`: Servis olarak calisma

## Yol Haritasi

- Lavalink node izleme ve otomatik saglik bildirimi
- Web tabanli yonetim paneli
- Sunucu bazli ayar paneli
- Daha gelismis izin sistemi
- Daha detayli muzik istatistikleri

## Yasal Sayfalar

- [Gizlilik Politikasi](./privacy.html)
- [Kullanim Kosullari](./terms.html)

## Gelistirici

<div align="center">

**Bogazitchy**

[![GitHub](https://img.shields.io/badge/GitHub-Bogazitchy-181717?style=for-the-badge&logo=github)](https://github.com/Bogazitchy)
[![Website](https://img.shields.io/badge/Web-itchy.com.tr-0A7B45?style=for-the-badge&logo=googlechrome&logoColor=white)](https://itchy.com.tr)

<sub>Hoslaf Bot, Discord sunucularinda temiz muzik deneyimi ve pratik bilgi komutlari icin gelistirilmistir.</sub>

</div>
