# Dokumentacija za razvijalce

## Kazalo

- [1. Dobrodošli](#1-dobrodošli)
- [2. Arhitektura sistema](#2-arhitektura-sistema)
- [3. Dokumentacija API](#3-dokumentacija-api)
- [4. Kako prispevati](#4-kako-prispevati)
- [5. Nasveti za delo z Dockerjem](#5-working-with-docker-tips)
- [6. Delo z avtomatiziranimi testi](#6-working-with-the-automated-tests)
- [7. Kako se pretvarja video](#7-how-video-is-transcoded)

## 1. Dobrodošli

Ta stran je namenjena razvijalcem MediaCMS in vsebuje povezane informacije.

## 2. Arhitektura sistema

bo napisano

## 3. Dokumentacija API

API je dokumentiran z uporabo Swaggerja – preverite na http://your_installation/swagger –
primer https://demo.mediacms.io/swagger/
Ta stran vam omogoča prijavo za izvajanje avtentificiranih dejanj – uporabila bo tudi vašo sejo, če ste prijavljeni.

Primer dela s knjižnico Python requests:

```
import requests

auth = ('user' ,'password')
upload_url = "https://domain/api/v1/media"
title = 'x title'
description = 'x description'
media_file = '/tmp/file.mp4'

requests.post(
    url=upload_url,
    files={'media_file': open(media_file,'rb')},
    data={'title': title, 'description': description},
    auth=auth
)
```

## 4. Kako prispevati

Preden pošljete PR, se prepričajte, da je vaš kod pravilno oblikovan. Za to uporabite `pre-commit install`, da namestite
pre-commit hook, in zaženite `pre-commit run --all` ter popravite vse, preden potrdite. Ta pre-commit bo vsakič, ko
potrdite kod, preveril vaš kod lint.

Če želite prispevati k temu repozitoriju, si oglejte [stran s kodeksom ravnanja](../CODE_OF_CONDUCT.md).

## 5. Nasveti za delo z Dockerjem

Za namestitev Dockerja sledite navodilom za namestitev Dockerja + Docker Compose (docs/Docker_Compose.md) in nato
zgradite/zaženite docker-compose-dev.yaml . To bo zagnalo frontend aplikacijo na vratih 8088 nad vsemi drugimi
kontejnerji (vključno z Django spletno aplikacijo na vratih 80).

```
docker compose -f docker-compose-dev.yaml build
docker compose -f docker-compose-dev.yaml up
```

Med namestitvijo se ustvari uporabnik `admin`. Njegove lastnosti so opredeljene v `docker-compose-dev.yaml`:

```
ADMIN_USER: 'admin'
ADMIN_PASSWORD: 'admin'
ADMIN_EMAIL: 'admin@localhost'
```

### Spremembe v frontend aplikaciji

Na primer, spremenite `frontend/src/static/js/pages/HomePage.tsx` , razvojna aplikacija se osveži v nekaj sekundah (
vroče ponovno nalaganje) in vidim spremembe. Ko sem zadovoljen, lahko zaženem

```
docker compose -f docker-compose-dev.yaml exec -T frontend npm run dist
```

Da bi bile spremembe vidne v aplikaciji, ko se prenašajo prek nginx,

```
cp -r frontend/dist/static/* static/
```

POST klici: jih ni mogoče izvesti prek razvojnega strežnika, ampak jih je treba izvesti prek običajne aplikacije (vrata

80) in nato spremembe videti v razvojni aplikaciji na vratih 8088.
    Preverite, ali so URL-ji nastavljeni v `frontend/.env`, če se razlikujejo od localhost

Stran medijev: vsebino je treba naložiti prek glavne aplikacije (nginx/vrata 80) in nato uporabiti ID za stran
media.html, na primer `http://localhost:8088/media.html?m=nc9rotyWP`

Rešiti je treba tudi nekaj težav s CORS, da bodo nekatere strani delovale, npr. stran za upravljanje komentarjev.

```
http://localhost:8088/manage-media.html manage_media
```

### Spremembe v ozadju aplikacije

Ko spremenim aplikacijo Django (npr. spremenim datoteko `files/forms.py`), moram za prikaz sprememb ponovno zagnati
spletni kontejner

```
docker compose -f docker-compose-dev.yaml restart web
```

## Kako se pretvori video

Izvirne datoteke se naložijo na aplikacijski strežnik, kjer se shranijo kot FileFields.

Če so datoteke videi in je njihova dolžina večja od določene vrednosti (določene v nastavitvah, 4min), se razdelijo na
dele, tako da je za vsak del en objekt Encode, za vse omogočene EncodeProfiles.

Nato delavci začnejo izbirati Encode objekte in pretvarjajo dele, tako da če je del pravilno pretvorjen, se izvirna
datoteka (majhen del) nadomesti s pretvorjeno datoteko, status Encode objekta pa se označi kot »uspešen«.

original.mp4 (1G, 720px)--> Encode1 (100MB, 240px, chunk=True), Encode2 (100MB, 240px, chunk=True)... EncodeXX (100 MB,
720 px, chunk=True) ---> ko so vsi objekti Encode uspešni, se za določeno ločljivost združijo v datoteko
original_resolution.mp4, ki se shrani kot objekt Encode (chunk=False). To je tisto, kar je na voljo za prenos.

Očitno se objekt Encode uporablja za shranjevanje kodiranih datotek, ki se na koncu predvajajo (chunk=False,
status="success"), pa tudi datotek, ki so v postopku pretvorbe (chunk=True, status="pending"").

(Odprta oklepaja)
obstaja tudi eksperimentalna majhna storitev (ki trenutno ni vključena v repozitorij), ki komunicira samo prek API-ja in
a) pridobi naloge za izvedbo, b) vrne rezultate. Torej, pošlje zahtevo in prejme ukaz ffmpeg ter datoteko, izvede ukaz
ffmpeg in vrne rezultat. Ta mehanizem sem uporabil v številnih namestitvah za migracijo obstoječih videov prek več
strežnikov/procesorjev in deloval je brez težav, razen ene, in sicer da je bilo treba nekatere začasne datoteke
odstraniti s strežnikov (prek periodične naloge, kar ni tako velik problem).
(Zapiranje oklepaja)

Ko je objekt Encode označen kot uspešen in chunk=False, in je tako na voljo za prenos/pretakanje, se zažene naloga, ki
shrani HLS različico datoteke (1 mp4-->x število majhnih .ts delcev). To bi bil FILES_C

Ta mehanizem omogoča delavcem, ki imajo dostop do istega datotečnega sistema (bodisi localhost ali prek skupnega
omrežnega datotečnega sistema, npr. NFS/EFS), da delajo istočasno in ustvarjajo rezultate.

## 6. Delo z avtomatiziranimi testi

Ta navodila predpostavljajo, da uporabljate namestitev docker.

    1. Zaženite docker-compose.

```
docker compose up
```

    2. Namestite zahteve iz `requirements-dev.txt ` na spletni kontejner (za to bomo uporabili spletni kontejner).

```
docker compose exec -T web pip install -r requirements-dev.txt
```

    3. Sedaj lahko zaženete obstoječe teste.

```
docker compose exec --env TESTING=True -T web pytest
```

`TESTING=True` se prenese, da Django ve, da gre za testno okolje (tako da na primer izvaja naloge Celery kot funkcije in
ne kot naloge v ozadju, saj Celery v primeru pytest ni zagnan).

    4. Poskusite lahko en sam test, tako da določite pot, na primer

```
docker compose exec --env TESTING=True -T web pytest tests/test_fixtures.py
```

    5. Ogledate si lahko tudi pokritost

```
docker compose exec --env TESTING=True -T web pytest --cov=. --cov-report=html
```
