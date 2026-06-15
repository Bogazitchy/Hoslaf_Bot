<div align="center">

<img src="./assets/hoslaf-banner.png" alt="Hoşlaf Bot banner" width="100%">

<br>

# HOŞLAF BOT

### Discord sunucuları için müzik, eğlence ve bilgi asistanı

<p>
  YouTube, Spotify ve SoundCloud desteğini; radyo, futbol, haber,
  yapay zekâ destekli arama ve tarih içerikleriyle tek botta buluşturur.
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/discord.py-2.7.1-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="discord.py 2.7.1">
  <img src="https://img.shields.io/badge/FFmpeg-Audio-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-222222?style=for-the-badge" alt="Windows ve Linux">
</p>

<p>
  <a href="#-özellikler">Özellikler</a> •
  <a href="#-komutlar">Komutlar</a> •
  <a href="#-kurulum">Kurulum</a> •
  <a href="#-yapılandırma">Yapılandırma</a> •
  <a href="#-servis-olarak-çalıştırma">Servis</a>
</p>

</div>

---

## Hoşlaf Bot Nedir?

Hoşlaf Bot, Discord topluluklarının günlük ihtiyaçlarını tek bir uygulamada
toplayan çok amaçlı bir bottur. Gelişmiş müzik kuyruğu ve kalıcı kontrol
panelinin yanında canlı skor, lig bilgileri, radyo, haber, web araması ve
tarihte bugün içerikleri sunar.

Botun müzik paneli aynı mesaj üzerinde güncellenir. Geçici komut yanıtları
otomatik temizlenir; böylece sohbet kanalı gereksiz bot mesajlarıyla dolmaz.

<div align="center">
  <img src="./assets/hoslaf-logo.png" alt="Hoşlaf Bot logo" width="360">
</div>

## Özellikler

<table>
  <tr>
    <td width="50%">
      <h3>🎵 Gelişmiş Müzik Sistemi</h3>
      YouTube, YouTube playlist, Spotify şarkı/playlist/albüm ve SoundCloud
      kaynaklarını destekler. Kuyruk ön yükleme, geçmiş, karıştırma, ses
      kontrolü ve ileri sarma özellikleri içerir.
    </td>
    <td width="50%">
      <h3>🎛️ Kalıcı Müzik Paneli</h3>
      Çalan şarkıyı, isteyen kullanıcıyı, süreyi, ses seviyesini ve kuyruğu
      tek panelde gösterir. Duraklat, devam et, atla, durdur ve ses
      kontrolleri Türkçe butonlarla sunulur.
    </td>
  </tr>
  <tr>
    <td>
      <h3>✨ Otomatik Öneri</h3>
      Kuyruk sona erdiğinde benzer parçalar bulabilir. Yakın geçmişte çalınan
      içerikleri mümkün olduğunca tekrar seçmez.
    </td>
    <td>
      <h3>📻 İnternet Radyosu</h3>
      Radio Browser üzerinden istasyon arar, sonuçları listeler ve seçilen
      canlı yayını doğrudan ses kanalında oynatır.
    </td>
  </tr>
  <tr>
    <td>
      <h3>⚽ Futbol Merkezi</h3>
      Günün maçları, canlı skorlar, lig bazlı karşılaşmalar, puan durumu ve
      Şampiyonlar Ligi turnuva ağacını gösterir.
    </td>
    <td>
      <h3>📰 Bilgi ve Gündem</h3>
      Türkiye gündeminden haberler, Exa AI destekli web araması ve Wikipedia
      tabanlı tarihte bugün içerikleri sağlar.
    </td>
  </tr>
  <tr>
    <td>
      <h3>📊 Kişisel Müzik Profili</h3>
      Kullanıcıların eklediği şarkı sayısını, toplam dinleme süresini ve en
      sık tercih edilen şarkı ve sanatçıları takip eder.
    </td>
    <td>
      <h3>🛡️ Sürekli Çalışma</h3>
      Windows servis dosyaları, otomatik başlatma görevleri ve çalışma
      günlükleriyle kesintisiz kullanım için hazırlanmıştır.
    </td>
  </tr>
</table>

## Müzik Paneli

Panel, her yeni komutta ayrı bir mesaj üretmek yerine mevcut mesajını
günceller. Böylece kanal düzenli kalırken kontroller her zaman erişilebilir
olur.

| Kontrol | İşlev |
| --- | --- |
| **Duraklat / Devam** | Oynatmayı duraklatır veya kaldığı yerden sürdürür. |
| **Atla** | Çalan parçayı geçip sıradaki parçaya devam eder. |
| **Durdur** | Kuyruğu temizler ve aktif oynatmayı güvenli biçimde sonlandırır. |
| **Ses - / Ses +** | Ses seviyesini panel üzerinden değiştirir. |

Panelde ayrıca şunlar gösterilir:

- Çalan parça ve bağlantısı
- Parçayı isteyen kullanıcı
- Parça süresi ve ses seviyesi
- Sıradaki parçaların özeti
- Toplam kuyruk süresi
- Otomatik öneri durumu

## Komutlar

### Müzik

| Komut | Açıklama |
| --- | --- |
| `/oynat sarki` | Şarkı adı veya desteklenen bağlantı üzerinden müzik çalar. |
| `/kapat` | Oynatmayı kapatır ve botu ses kanalından çıkarır. |
| `/atla miktar` | Çalan parçayı veya belirtilen sayıda parçayı atlar. |
| `/duraklat` | Aktif parçayı duraklatır. |
| `/devam` | Duraklatılan parçayı devam ettirir. |
| `/sardir saniye` | Parçayı belirtilen saniyeye taşır. |
| `/karistir` | Bekleyen müzik kuyruğunu karıştırır. |
| `/ses seviye` | Ses seviyesini 0-100 arasında ayarlar. |
| `/kuyruk` | Çalan parça ve sıradaki parçaları gösterir. |
| `/gecmis` | Son çalınan parçaları listeler. |
| `/otomatik ac\|kapat` | Kuyruk sonrası otomatik öneriyi yönetir. |
| `/muzikprofil` | Kullanıcının müzik istatistiklerini gösterir. |
| `/lyrics` | Çalan parçanın sözlerini getirir. |

> Discord slash komutları Türkçe karakter kabul etmediği için `gecmis`,
> `sardir` ve `muzikprofil` gibi komutlar ASCII karakterlerle yazılır.

### Radyo

| Komut | Açıklama |
| --- | --- |
| `/radyo isim` | İstasyon arar ve en uygun sonucu oynatır. |
| `/radyolar isim` | Eşleşen radyo istasyonlarını seçim listesiyle gösterir. |

```text
/radyo Kral FM
/radyo Power FM
/radyolar rock
```

### Futbol

| Komut | Açıklama |
| --- | --- |
| `/bugun` | Bugünün maç takvimini gösterir. |
| `/canli` | Devam eden karşılaşmaların canlı skorlarını gösterir. |
| `/lig lig` | Seçilen ligin bugünkü maçlarını listeler. |
| `/puandurumu lig` | Seçilen ligin puan durumunu gösterir. |
| `/turnuva` | Şampiyonlar Ligi turnuva ağacını gösterir. |

Desteklenen organizasyonlar: Premier League, La Liga, Bundesliga, Serie A,
Ligue 1 ve UEFA Şampiyonlar Ligi.

### Haber, Arama ve Tarih

| Komut | Açıklama |
| --- | --- |
| `/haber` | Türkiye gündeminden güncel haberleri getirir. |
| `/ara sorgu` | Exa AI üzerinden web araması yapar. |
| `/tarihtebugun` | Bugünün tarihsel olaylarını gösterir. |
| `/tarihsorgu ay gun` | Belirli bir tarihte yaşanan olayları getirir. |
| `/rastgeletarih` | Rastgele bir güne ait tarihsel olayları gösterir. |

## Kurulum

### Gereksinimler

- Python 3.10 veya üzeri
- FFmpeg
- Discord uygulaması ve bot tokenı
- Kullanılacak özelliklere ait API anahtarları
- Sesli bağlantı için Discord botunda gerekli izinler

### 1. Depoyu Klonla

```bash
git clone https://github.com/Bogazitchy/Hoslaf_Bot.git
cd Hoslaf_Bot
```

### 2. Sanal Ortamı Oluştur

**Windows**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Linux**

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

### 3. FFmpeg'i Hazırla

FFmpeg sistem PATH değişkeninde bulunabilir veya çalıştırma ortamına uygun
biçimde proje tarafından erişilebilir olmalıdır.

Kontrol:

```bash
ffmpeg -version
```

### 4. Botu Başlat

**Windows**

```powershell
.\.venv\Scripts\python.exe bot.py
```

**Linux**

```bash
./.venv/bin/python bot.py
```

## Yapılandırma

Proje kökünde `.env` dosyası oluştur:

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

| Değişken | Kullanım |
| --- | --- |
| `DISCORD_TOKEN` | Discord botunun kimlik doğrulaması |
| `SPOTIFY_CLIENT_ID` | Spotify katalog erişimi |
| `SPOTIFY_CLIENT_SECRET` | Spotify uygulama doğrulaması |
| `SPOTIFY_REDIRECT_URI` | Kullanıcı playlist yetkilendirme dönüş adresi |
| `GENIUS_TOKEN` | Şarkı sözü araması |
| `EXA_API_KEY` | Yapay zekâ destekli web araması |
| `APIF_KEY` | API-Football canlı maç verileri |
| `FD_KEY` | Football-Data lig ve puan durumu verileri |

### API Panelleri

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Spotify for Developers](https://developer.spotify.com/dashboard)
- [Genius API](https://genius.com/api-clients)
- [Exa Dashboard](https://dashboard.exa.ai)
- [API-Football](https://api-sports.io)
- [Football-Data](https://www.football-data.org)

## Spotify Playlist Yetkilendirmesi

Bazı Spotify playlistleri kullanıcı yetkilendirmesi gerektirir.

1. Spotify Developer Dashboard içinde Redirect URI olarak
   `http://127.0.0.1:8888/callback` adresini ekle.
2. Yetkilendirme aracını çalıştır:

```powershell
.\.venv\Scripts\python.exe spotify_authorize.py
```

3. Terminalde verilen bağlantıyı tarayıcıda aç ve Spotify izin ekranını onayla.
4. Yönlendirildiğin tam adresi terminale yapıştır.

Başarılı işlem sonunda `.spotify_user_cache` oluşturulur. Bu dosya gizlidir
ve Git deposuna yüklenmemelidir.

## Servis Olarak Çalıştırma

### Windows

Depoda WinSW tabanlı servis yapılandırması ve otomatik başlatma yardımcıları
bulunur. `HoslafBotService.exe` güvenlik ve boyut nedeniyle repoya eklenmez.

1. WinSW x64 sürümünü indir.
2. Dosyayı `HoslafBotService.exe` olarak yeniden adlandır.
3. Proje köküne yerleştir.
4. Yönetici PowerShell aç ve çalıştır:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install_hoslafbot_service.ps1
.\register_hoslafbot_startup_task.ps1
```

Servis kontrolü:

```powershell
sc.exe query HoslafBot
sc.exe qc HoslafBot
```

Günlük dosyaları:

```text
logs/hoslafbot-runner.log
logs/hoslafbot-process.out.log
logs/hoslafbot-process.err.log
```

## Proje Yapısı

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

## Güvenlik

- `.env` dosyasını ve Discord tokenını hiçbir zaman paylaşma.
- Token yanlışlıkla açığa çıktıysa Discord Developer Portal üzerinden hemen
  yenile.
- `.spotify_user_cache` ve `.spotify_client_cache` dosyalarını repoya ekleme.
- `music_stats.json` kullanıcı istatistikleri içerdiğinden gizli tutulur.
- Log dosyalarını paylaşmadan önce token, kullanıcı ve sunucu bilgilerini
  kontrol et.
- Bot hesabına yalnızca ihtiyaç duyduğu Discord izinlerini ver.

`.gitignore` bu çalışma zamanı dosyalarını varsayılan olarak dışarıda tutar.

## Kullanılan Teknolojiler

<p>
  <img src="https://skillicons.dev/icons?i=python,discord,git,github,powershell" alt="Kullanılan teknolojiler">
</p>

- **discord.py**: Discord API, slash komutlar ve etkileşimli bileşenler
- **yt-dlp + FFmpeg**: Medya çözümleme ve ses aktarımı
- **Spotipy**: Spotify içerik çözümleme
- **aiohttp + requests**: Harici servis bağlantıları
- **Genius API**: Şarkı sözleri
- **Exa AI**: Web araması
- **API-Football / Football-Data**: Futbol verileri
- **WinSW + PowerShell**: Windows servis yönetimi

## Yasal Sayfalar

- [Gizlilik Politikası](./privacy.html)
- [Kullanım Koşulları](./terms.html)

## Geliştirici

<div align="center">

**Bogazitchy**

[![GitHub](https://img.shields.io/badge/GitHub-Bogazitchy-181717?style=for-the-badge&logo=github)](https://github.com/Bogazitchy)
[![Website](https://img.shields.io/badge/Web-itchy.com.tr-0A7B45?style=for-the-badge&logo=googlechrome&logoColor=white)](https://itchy.com.tr)

<sub>Hoşlaf Bot, topluluk deneyimini sade ve güçlü araçlarla geliştirmek için hazırlanmıştır.</sub>

</div>
