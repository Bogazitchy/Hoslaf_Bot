# Hoşlaf Bot

Hoşlaf Bot; Discord sunucuları için hazırlanmış çok amaçlı bir bottur. Müzik çalma, Spotify/YouTube playlist desteği, radyo, futbol takibi, haberler, web araması ve tarihte bugün özelliklerini tek dosyada toplar.

## Özellikler

- **Müzik oynatma:** YouTube, YouTube playlist, Spotify şarkı, Spotify playlist/album ve SoundCloud desteği.
- **Müzik paneli:** Çalan şarkı, kuyruk, ses seviyesi, isteyen kişi ve otomatik öneri durumunu tek mesajda gösterir.
- **Panel butonları:** Pause/Resume, Skip, Stop, Queue, Vol -, Vol +.
- **Akıllı kuyruk:** Kuyruk, geçmiş, toplam süre, isteyen kişi bilgisi ve shuffle desteği.
- **Otomatik öneri:** Kuyruk bitince benzer şarkı bulur; son çalınanlara benzeyen şarkıları tekrar açmamaya çalışır.
- **Müzik profili:** Kullanıcı bazlı şarkı sayısı, toplam süre, en çok eklenen şarkılar ve sanatçı/kanal istatistikleri.
- **Radyo:** Radio Browser üzerinden radyo arama ve canlı yayın çalma.
- **Futbol:** Günlük maçlar, canlı skorlar, lig fikstürü, puan durumu ve turnuva ağacı.
- **Haber:** Türkiye gündeminden haber çekme ve zamanlı paylaşım.
- **Web araması:** Exa AI destekli arama.
- **Tarihte bugün:** Wikipedia tabanlı tarih olayları.
- **Windows servis desteği:** WinSW ile arka planda otomatik çalışan servis kurulumu.

## Gereksinimler

- Python 3.10+
- ffmpeg
- Discord bot token
- Gerekli API anahtarları
- Windows servis kurulumu için WinSW

## Kurulum

```bash
git clone https://github.com/Bogazitchy/Hoslaf_Bot.git
cd Hoslaf_Bot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Linux/macOS için:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## Ortam Değişkenleri

Proje klasöründe `.env` dosyası oluştur:

```env
DISCORD_TOKEN=discord_bot_token
SPOTIFY_CLIENT_ID=spotify_client_id
SPOTIFY_CLIENT_SECRET=spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
GENIUS_TOKEN=genius_token
EXA_API_KEY=exa_api_key
APIF_KEY=api_football_key
FD_KEY=football_data_key
```

`.env`, Spotify cache dosyaları, loglar ve kullanıcı müzik istatistikleri git'e yüklenmez.

## Botu Çalıştırma

```bash
.\.venv\Scripts\python.exe bot.py
```

Linux/macOS:

```bash
./.venv/bin/python bot.py
```

## Spotify Playlist Yetkilendirme

Spotify'ın bazı playlistleri okuyabilmesi için kullanıcı yetkilendirmesi gerekir.

1. Spotify Developer Dashboard içinde Redirect URI olarak şunu ekle:

```text
http://127.0.0.1:8888/callback
```

2. Yetkilendirme scriptini çalıştır:

```bash
.\.venv\Scripts\python.exe spotify_authorize.py
```

3. Çıkan linki tarayıcıda aç, Spotify izin ekranını onayla.
4. Tarayıcının yönlendiği tam URL'yi terminale yapıştır.

Bu işlem `.spotify_user_cache` dosyasını oluşturur.

## Windows Servis Kurulumu

Bu repo Windows servis ayar dosyalarını içerir, ancak WinSW exe dosyası repoya eklenmez.

1. WinSW x64 exe dosyasını indir.
2. Dosya adını `HoslafBotService.exe` yap.
3. Proje klasörüne koy.
4. Yönetici PowerShell aç.
5. Kurulumu çalıştır:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install_hoslafbot_service.ps1
.\register_hoslafbot_startup_task.ps1
```

Servis adı: `HoslafBot`

Kontrol:

```powershell
sc.exe query HoslafBot
sc.exe qc HoslafBot
```

Loglar:

```text
logs/hoslafbot-runner.log
logs/hoslafbot-process.out.log
logs/hoslafbot-process.err.log
```

## Müzik Komutları

| Komut | Açıklama |
| --- | --- |
| `/oynat sarki` | Şarkı adı, YouTube, Spotify veya SoundCloud linki ile çalar. Playlist desteği vardır. |
| `/kapat` | Müziği kapatır ve ses kanalından çıkar. |
| `/atla miktar` | Çalan şarkıyı veya belirtilen miktarda şarkıyı atlar. |
| `/duraklat` | Şarkıyı duraklatır. |
| `/devam` | Duraklatılan şarkıyı devam ettirir. |
| `/sardir saniye` | Şarkıyı belirtilen saniyeye sarar. |
| `/karistir` | Kuyruğu karıştırır. |
| `/ses seviye` | Ses seviyesini 0-100 arasında ayarlar. |
| `/kuyruk` | Kuyruğu embed olarak gösterir. |
| `/gecmis` | Son çalınan şarkıları gösterir. |
| `/otomatik ac` | Kuyruk bitince otomatik öneriyi açar. |
| `/otomatik kapat` | Otomatik öneriyi kapatır. |
| `/muzikprofil` | Kullanıcının müzik istatistiklerini gösterir. |
| `/lyrics` | Çalan şarkının sözlerini getirir. |

Not: Discord slash komut adlarında Türkçe karakter desteklenmediği için `gecmis`, `muzikprofil`, `sardir` gibi ASCII komut adları kullanılır.

## Radyo Komutları

| Komut | Açıklama |
| --- | --- |
| `/radyo isim` | Radyo adıyla arama yapar ve en iyi sonucu çalar. |
| `/radyolar isim` | Radyo arama sonuçlarını listeler. |

Örnek:

```text
/radyo Kral FM
/radyo Power FM
/radyolar rock
```

## Futbol Komutları

| Komut | Açıklama |
| --- | --- |
| `/bugun` | Bugünkü maç takvimini gösterir. |
| `/canli` | Canlı maç skorlarını gösterir. |
| `/lig lig` | Seçilen ligin bugünkü maçlarını gösterir. |
| `/puandurumu lig` | Seçilen ligin puan durumunu gösterir. |
| `/turnuva` | Şampiyonlar Ligi turnuva ağacını gösterir. |

Desteklenen ligler:

- Premier League
- La Liga
- Bundesliga
- Serie A
- Ligue 1
- Şampiyonlar Ligi

## Haber ve Arama Komutları

| Komut | Açıklama |
| --- | --- |
| `/haber` | Türkiye gündeminden haber getirir. |
| `/ara sorgu` | Exa AI ile web araması yapar. |

## Tarihte Bugün Komutları

| Komut | Açıklama |
| --- | --- |
| `/tarihtebugun` | Bugün yaşanan tarih olaylarını gösterir. |
| `/tarihsorgu ay gün` | Belirli tarihteki olayları gösterir. |
| `/rastgeletarih` | Rastgele bir tarihteki olayları gösterir. |

## API Anahtarları

| Servis | Adres |
| --- | --- |
| Discord Bot Token | https://discord.com/developers/applications |
| Spotify Client ID/Secret | https://developer.spotify.com/dashboard |
| Genius Token | https://genius.com/api-clients |
| Exa API Key | https://dashboard.exa.ai |
| API-Football Key | https://api-sports.io |
| Football-Data Key | https://www.football-data.org |

## Dosya Yapısı

```text
Hoslaf_Bot/
├── bot.py
├── requirements.txt
├── spotify_authorize.py
├── HoslafBotService.xml
├── install_hoslafbot_service.ps1
├── run_hoslafbot_service.ps1
├── ensure_hoslafbot_service.ps1
├── register_hoslafbot_startup_task.ps1
├── terms.html
├── privacy.html
└── README.md
```

## Güvenlik Notları

- `.env` dosyasını repoya yükleme.
- `.spotify_user_cache`, `.spotify_client_cache`, `music_stats.json` ve `logs/` çalışma zamanı dosyalarıdır.
- `HoslafBotService.exe` ve `ffmpeg.exe` binary dosyaları repoya eklenmez.

## Geliştirici

Bogazitchy - https://github.com/Bogazitchy
