# Pretvorba v MediaCMS

MediaCMS uporablja FFmpeg za pretvorbo medijskih datotek. Večina nastavitev in konfiguracij pretvorbe je opredeljenih v `files/helpers.py`.

## Možnosti konfiguracije

V `cms/settings.py` je mogoče prilagoditi več parametrov pretvorbe:

### FFmpeg Preset

Privzeta nastavitev FFmpeg je nastavljena na »medium«. Ta nastavitev nadzira kompromis med hitrostjo kodiranja in učinkovitostjo stiskanja.

```python
# ffmpeg options
FFMPEG_DEFAULT_PRESET = "medium" # glej https://trac.ffmpeg.org/wiki/Encode/H.264
```

Na voljo so naslednje prednastavitve:
- ultrafast
- superfast
- veryfast
- faster
- fast
- medium (privzeto)
- slow
- slower
- veryslow

Hitrejše prednastavitve povzročijo večje datoteke za enako kakovost, medtem ko počasnejše prednastavitve zagotavljajo boljšo stiskanje, vendar traja kodiranje dlje.

### Druge nastavitve pretvorbe

Dodatne nastavitve pretvorbe v `settings.py` vključujejo:

- `FFMPEG_COMMAND`: Pot do izvedljive datoteke FFmpeg
- `FFPROBE_COMMAND`: Pot do izvedljive datoteke FFprobe
- `DO_NOT_TRANSCODE_VIDEO`: Če je nastavljeno na True, se prikaže samo izvirni video brez pretvorbe
- `CHUNKIZE_VIDEO_DURATION`: Videi, ki so daljši od te trajanosti (v sekundah), se razdelijo na dele in kodirajo neodvisno
- `VIDEO_CHUNKS_DURATION`: Trajanje vsakega dela (mora biti krajše od CHUNKIZE_VIDEO_DURATION)
- `MINIMUM_RESOLUTIONS_TO_ENCODE`: Vedno kodirajte te ločljivosti, tudi če je potrebno povečanje ločljivosti

## Napredna konfiguracija

Za naprednejše nastavitve pretvorbe boste morda morali spremeniti naslednje v `files/helpers.py`:

- Video bitrate za različne kodeke in ločljivosti
- Avdio kodirnike in bitrate
- Vrednosti CRF (Constant Rate Factor)
- Nastavitve ključnih okvirov
- Parametre kodiranja za različne kodeke (H.264, H.265, VP9)
