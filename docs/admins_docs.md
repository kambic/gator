# Dokumentacija za administratorje

## Kazalo

- [1. Dobrodošli](#1-dobrodošli)
- [2. Namestitev na enem strežniku](#2-namestitev-na-enem-strežniku)
- [3. Namestitev Dockerja](#3-namestitev-dockerja)
- [4. Možnosti razporeditve Dockerja](#4-moznosti-razporeditve-dockerja)
- [5. Konfiguracija](#5-konfiguracija)
- [6. Upravljanje strani](#6-upravljanje-strani)
- [7. Nadzorna plošča Django](#7-nadzorna-plosca-django)
- [8. O delovnem toku portala](#8-o-delovnem-toku-portala)
- [9. O vlogah uporabnikov](#9-o-vlogah-uporabnikov)
- [10. Dodajanje jezikov za napise in podnapise](#10-dodajanje-jezikov-za-napise-in-podnapise)
- [11. Dodajanje/brisanje kategorij in oznak](#11-dodajanjebrisanje-kategorij-in-oznak)
- [12. Pretvorba videa](#12-pretvorba-videa)
- [13. Kako dodati statično stran v stranski vrstici](#13-kako-dodati-staticno-stran-v-stranski-vrstici)
- [14. Dodajte Google Analytics](#14-dodajte-google-analytics)
- [15. Odpravljanje težav z e-pošto](#15-odpravljanje-tezav-z-e-posto)
- [16. Pogosta vprašanja](#16-pogosta-vprasanja)
- [17. Koda za soglasje s piškotki](#17-koda-za-soglasje-s-piskotki)
- [18. Onemogočite kodiranje in prikažite samo izvirno datoteko](#18-onemogocite-kodiranje-in-prikazite-samo-izvirno-datoteko)
- [19. Zaobljeni koti na videih](#19-zaobljeni-koti-na-videih)
- [20. Prevajanje](#20-prevajanje)
- [21. Kako spremeniti okvirje videov](#21-kako-spremeniti-okvirje-videov)
- [22. Nadzor dostopa na podlagi vlog](#22-nadzor-dostopa-na-podlagi-vlog)
- [23. Nastavitev SAML](#23-nastavitev-saml)
- [24. Nastavitev ponudnikov identitete](#24-nastavitev-ponudnikov-identitete)
- [25. Prilagojene URL-je](#25-prilagojene-url-je)
- [26. Dovoljene datoteke](#26-dovoljene-datoteke)
- [27. Omejitve nalaganja za uporabnike](#27-omejitve-nalaganja-za-uporabnike)
- [28. Whisper Transcribe za samodejne podnapise](#28-whisper-transcribe-za-samodejne-podnapise)

## 1. Dobrodošli

Ta stran je namenjena administratorjem MediaCMS, ki so odgovorni za namestitev programske opreme, njeno vzdrževanje in
spreminjanje.

## 2. Namestitev na enem strežniku

Osnovne odvisnosti so python3, Django, celery, PostgreSQL, redis, ffmpeg. MediaCMS lahko deluje na katerem koli sistemu,
na katerem so nameščene te odvisnosti. Vendar je install.sh preizkušen le v različicah Linux Ubuntu 24 in 22.

Namestitev na sistemu Ubuntu 22/24 z nameščenim programom git naj bi bila končana v nekaj minutah z naslednjimi koraki.
Prepričajte se, da ga izvajate kot uporabnik root na čistem sistemu, saj bo avtomatski skript namestil in konfiguriral
naslednje storitve: Celery/PostgreSQL/Redis/Nginx in nadomestil vse obstoječe nastavitve.

```bash
mkdir /home/mediacms.io && cd /home/mediacms.io/
git clone https://github.com/mediacms-io/mediacms
cd /home/mediacms.io/mediacms/ && bash ./install.sh
```

Scenarij vas bo vprašal, ali imate URL, na katerem želite namestiti MediaCMS, sicer bo uporabil localhost.
Če navedete URL, bo za namestitev veljavnega SSL certifikata uporabil storitev Let's Encrypt.

### Update

Če ste za namestitev MediaCMS uporabili zgornji način, posodobite z naslednjim:

```bash
cd /home/mediacms.io/mediacms # enter mediacms directory
source  /home/mediacms.io/bin/activate # use virtualenv
git pull # update code
pip install -r requirements.txt -U # run pip install to update
python manage.py migrate # run Django migrations
sudo systemctl restart mediacms celery_long celery_short # restart services
```

### Konfiguracija

Preverite konfiguracijski razdelek tukaj.

### Vzdrževanje

Bazo podatkov lahko varnostno kopirate s pg_dump, medijske datoteke v /home/mediacms.io/mediacms/media_files pa
vključujejo izvirne datoteke in kodirane/prekodirane različice.

## 3. Namestitev Dockerja

## Namestitev

Namestite najnovejšo različico [Dockerja](https://docs.docker.com/get-docker/)
in [Docker Compose](https://docs.docker.com/compose/install/).

Nato kot root zaženite

```bash
git clone https://github.com/mediacms-io/mediacms
cd mediacms
```

Privzeta možnost je, da MediaCMS deluje na vseh IP-naslovih, ki so na voljo na strežniku (vključno z localhost).
Če želite raziskati več možnosti (vključno z nastavitvijo https s certifikatom letsencrypt), si oglejte
razdelek [Docker deployment](/docs/admins_docs.md#4-docker-deployment-options) za različne nastavitve docker-compose, ki
jih lahko uporabite.

```bash
docker compose up
```

S tem se bodo prenesle vse slike Dockerja, povezane z MediaCMS, in zagnali vsi kontejnerji. Ko bo postopek končan, bo
MediaCMS nameščen in dostopen na http://localhost ali http://ip

Ustvarjen je bil uporabnik admin z naključnim geslom, ki ga lahko vidite na koncu kontejnerja migracij, npr.

```
migrations_1     | Created admin user with password: gwg1clfkwf
```

ali če ste nastavili spremenljivko ADMIN_PASSWORD v datoteki docker-compose, ki ste jo uporabili (na primer
`docker-compose.yaml`), bo ta spremenljivka nastavljena kot geslo skrbnika

`Opomba`: če želite uporabljati samodejne transkripcije, morate storiti eno od naslednjega:

* uporabite docker-compose.full.yaml, v tem primeru pa zaženite
  `docker-compose -f docker-compose.yaml -f docker-compose.full.yaml up`
* ali uredite datoteko docker-compose.yaml in nastavite sliko za storitev celery_worker kot mediacms/mediacms:full
  namesto mediacms/mediacms:latest

Poleg tega nastavite spremenljivko `USE_WHISPER_TRANSCRIBE = True` v datoteki settings.py

### Posodobitev

Prenesite najnovejšo sliko MediaCMS in ustavite/zaženite kontejnerje

```bash
cd /path/to/mediacms/installation
docker pull mediacms/mediacms
docker compose down
docker compose up
```

## Konfiguracija

Preverite dokumentacijo o konfiguraciji tukaj.

### Vzdrževanje

Baza podatkov je shranjena v ../postgres_data/, medijske datoteke pa v media_files/.

## 4. Možnosti razporeditve Docker

Podoba mediacms je zasnovana tako, da kot glavni proces uporablja supervisord, ki upravlja eno ali več storitev,
potrebnih za zagon mediacms. S pomočjo spodnjih spremenljivk okolja, ki jih nastavimo na »yes« ali »no«, lahko izberemo,
katere storitve se izvajajo v danem kontejnerju:

* ENABLE_UWSGI
* ENABLE_NGINX
* ENABLE_CELERY_BEAT
* ENABLE_CELERY_SHORT
* ENABLE_CELERY_LONG
* ENABLE_MIGRATIONS

Privzeto so vse te storitve omogočene, vendar je za ustvarjanje prilagodljive razporeditve mogoče nekatere od njih
onemogočiti in storitev razdeliti na manjše storitve.

Glejte tudi `Dockerfile` za druge spremenljivke okolja, ki jih morda želite prepisati. Nastavitve aplikacije, npr.
`FRONTEND_HOST`, lahko prepišete tudi z posodobitvijo datoteke `deploy/docker/local_settings.py`.

Za zagon posodobite zgornje konfiguracije, če je potrebno, zgradite sliko z izvedbo `docker compose build`, nato pa
izvedite `docker compose run`.

### Enostavna namestitev, dostopna na naslovu http://localhost

Glavni kontejner izvaja migracije, mediacms_web, celery_beat, celery_workers (storitve celery_short in celery_long), ki
so dostopne na vratih 80, podprtih z redis in postgres podatkovno bazo.

FRONTEND_HOST v `deploy/docker/local_settings.py` je konfiguriran kot http://localhost na gostiteljskem računalniku
docker.

### Strežnik s certifikatom SSL prek storitve letsencrypt, dostopen na naslovu https://my_domain.com

Preden to preizkusite, se prepričajte, da IP kaže na my_domain.com.

Pri tej metodi se uporablja [ta razporeditev](../docker-compose-letsencrypt.yaml).

Uredite to datoteko in nastavite `VIRTUAL_HOST` kot my_domain.com, `LETSENCRYPT_HOST` kot my_domain.com in vaš e-poštni
naslov v `LETSENCRYPT_EMAIL`

Uredite `deploy/docker/local_settings.py` in nastavite https://my_domain.com kot `FRONTEND_HOST`

Sedaj zaženite `docker compose -f docker-compose-letsencrypt.yaml up`, ko se namestitev konča, boste lahko dostopali
do https://my_domain.com z veljavnim certifikatom Letsencrypt!

### Napredna namestitev, dostopna na naslovu http://localhost:8000

Tukaj lahko zaženemo 1 primer medijske storitve mediacms_web, pri čemer je FRONTEND_HOST v
`deploy/docker/local_settings.py` nastavljen kot http://localhost:8000. To se zagoni z enim primerom migracij in podpira
en primer celery_beat ter 1 ali več primerov celery_worker. Za vztrajnost se uporabljajo tudi kontejnerji Redis in
postgres. Stranke lahko dostopajo do storitve na http://localhost:8000, na gostiteljskem računalniku docker. To je
podobno [tej razporeditvi](../docker-compose.yaml), s `port`, ki je opredeljen v FRONTEND_HOST.

### Napredna razporeditev z obratnim proxyjem, dostopna kot http://mediacms.io

Tukaj lahko uporabimo `jwilder/nginx-proxy` za reverzni proxy do ene ali več primerov mediacms_web, ki jih podpirajo
druge storitve, kot je navedeno v prejšnji razporeditvi. FRONTEND_HOST v `deploy/docker/local_settings.py` je
konfiguriran kot http://mediacms.io, nginx-proxy ima odprto vrata 80. Stranke lahko dostopajo do storitve
na http://mediacms.io (če je DNS ali datoteka gostiteljev pravilno nastavljena, da kaže na IP naslova instance
nginx-proxy). To je podobno [tej razporeditvi](../docker-compose-http-proxy.yaml).

### Napredna namestitev z obratnim proxyjem, dostopna na naslovu https://localhost

Obratni proxy (`jwilder/nginx-proxy`) je mogoče konfigurirati tako, da zagotavlja SSL-prekinitev z uporabo
samopodpisanih certifikatov, certifikatov letsencrypt ali certifikatov, podpisanih s strani certifikacijske agencije (
glej: https://hub.docker.com/r/jwilder/nginx-proxy
ali [LetsEncrypt Example](https://www.singularaspect.com/use-nginx-proxy-and-letsencrypt-companion-to-host-multiple-websites/) ).
V tem primeru je treba FRONTEND_HOST nastaviti na https://mediacms.io. To je
podobno [tej razporeditvi](../docker-compose-http-proxy.yaml).

### Razširljiva arhitektura razporeditve (Docker, Swarm, Kubernetes)

Spodnja arhitektura posplošuje vse zgornje scenarije razporeditve in zagotavlja konceptualni načrt za druge
razporeditve, ki temeljijo na kubernetes in docker swarm. Omogoča horizontalno razširljivost z uporabo več primerov
mediacms_web in celery_workers. Za velike razporeditve se lahko uporabijo upravljani postgres, redis in shranjevanje.

![MediaCMS](images/architecture.png)

## 5. Konfiguracija

V datoteki `cms/settings.py` je na voljo več možnosti, kjer je opisano večino stvari, ki so dovoljene ali prepovedane.

Priporočljivo je, da jih nadomestite tako, da jih dodate v datoteko `local_settings.py` .

V primeru namestitve na enem strežniku dodajte v datoteko `cms/local_settings.py` .

V primeru namestitve docker compose dodajte v `deploy/docker/local_settings.py` . To bo samodejno prepisalo
`cms/local_settings.py` .

Vsaka sprememba zahteva ponovni zagon MediaCMS, da začne veljati.

Namestitev na enem strežniku: uredite `cms/local_settings.py`, naredite spremembo in ponovno zaženite MediaCMS.

```bash
#systemctl restart mediacms
```

Namestitev Docker Compose: uredite `deploy/docker/local_settings.py`, naredite spremembo in ponovno zaženite kontejnerje
MediaCMS

```bash
#docker compose restart web celery_worker celery_beat
```

### 5.1 Sprememba logotipa portala

Poiščite privzete svg datoteke za belo temo v `static/images/logo_dark.svg` in za temno temo v
`static/images/logo_light.svg`
Nove svg poti lahko določite z urejanjem spremenljivk `PORTAL_LOGO_DARK_SVG` in `PORTAL_LOGO_LIGHT_SVG` v `settings.py`.

Uporabite lahko tudi prilagojene png datoteke, tako da nastavite spremenljivki `PORTAL_LOGO_DARK_PNG` in
`PORTAL_LOGO_LIGHT_PNG` v `settings.py`. Svg datoteke imajo prednost pred png datotekami, zato bodo uporabljene svg
datoteke, če so nastavljene obe.

V vsakem primeru poskrbite, da so datoteke shranjene v mapi static/images.

### 5.2 Nastavite globalni naslov portala

nastavite `PORTAL_NAME`, npr.

```
PORTAL_NAME = ‚my awesome portal‘
```

### 5.3 Nadzorujte, kdo lahko dodaja medije

Privzeto `CAN_ADD_MEDIA = „all“` pomeni, da lahko vsi registrirani uporabniki dodajajo medije. Druge veljavne možnosti
so:

- **email_verified**, uporabnik mora ne le registrirati račun, ampak tudi potrditi e-poštni naslov (s klikom na
  povezavo, poslano ob registraciji). Očitno mora konfiguracija e-pošte delovati, sicer uporabniki ne bodo prejemali
  e-pošte.

- **advancedUser**, samo uporabniki, ki so označeni kot napredni uporabniki, lahko dodajajo medijske vsebine. Skrbniki
  ali upravitelji MediaCMS lahko uporabnike naredijo za napredne uporabnike tako, da uredijo njihov profil in izberejo
  advancedUser.

### 5.4 Kaj je portalni delovni tok

Spremenljivka `PORTAL_WORKFLOW` določa, kaj se zgodi z novo naloženimi mediji, ali se prikažejo na seznamih (kot
indeksna stran ali iskanje)

- **public** je privzeta možnost in pomeni, da se medij lahko prikaže na seznamih. Če je medij tipa video, se prikaže,
  ko je vsaj ena naloga, ki ustvari kodirano različico datoteke, uspešno zaključena. Drugi tipi datotek, kot so
  slike/avdio datoteke, se prikažejo takoj

- **private** pomeni, da je novo naložena vsebina zasebna – vidijo jo lahko samo uporabniki ali uredniki, upravitelji in
  skrbniki MediaCMS. Ti lahko status nastavijo tudi na javno ali neobjavo.

- **neobjavo** pomeni, da elementi niso objavljeni. Če pa uporabnik obišče url neobjavljenega medija, se bo ta
  prikazal (v nasprotju z zasebnim).

### 5.5 Prikaz ali skritje gumba Prijava

za prikaz gumba:

```
LOGIN_ALLOWED = True
```

za skritje gumba:

```
LOGIN_ALLOWED = False
```

### 5.6 Prikaz ali skritje gumba Registriraj se

za prikaz gumba:

```
REGISTER_ALLOWED = True
```

za skritje gumba:

```
REGISTER_ALLOWED = False
```

### 5.7 Prikaz ali skritje gumba za nalaganje medijev

Za prikaz:

```
UPLOAD_MEDIA_ALLOWED = True
```

Za skritje:

```
UPLOAD_MEDIA_ALLOWED = False
```

### 5.8 Prikaz ali skritje gumbov za dejanja (všeč mi je/ne všeč mi je/prijavi)

Spremenite (True/False) katero koli od naslednjih nastavitev:

```
- CAN_LIKE_MEDIA = True  # ali se prikaže všeč mi je medij
- CAN_DISLIKE_MEDIA = True  # ali se prikaže ne všeč mi je medij
- CAN_REPORT_MEDIA = True  # ali se prikaže prijavite medij
- CAN_SHARE_MEDIA = True  # ali se prikaže delite medij
```

### 5.9 Prikaz ali skritje možnosti prenosa na mediju

Uredite `templates/config/installation/features.html` in nastavite

```
download: false
```

### 5.10 Samodejno skritje medija ob prijavi

nastavite nizko število za spremenljivko `REPORTED_TIMES_THRESHOLD`
npr.

```
REPORTED_TIMES_THRESHOLD = 2
```

ko je meja dosežena, medij preide v zasebno stanje in upraviteljem se pošlje e-poštno sporočilo

### 5.11 Nastavite prilagojeno sporočilo na strani za nalaganje medijev

to sporočilo se prikaže pod obrazcem za povleci in spusti medij

```
PRE_UPLOAD_MEDIA_MESSAGE = ‚prilagojeno sporočilo‘
```

### 5.12 Nastavite nastavitve e-pošte

Nastavite pravilne nastavitve za posameznega ponudnika

```
DEFAULT_FROM_EMAIL = ‚info@mediacms.io‘
EMAIL_HOST_PASSWORD = ‚xyz‘
EMAIL_HOST_USER = ‚info@mediacms.io‘
EMAIL_USE_TLS = True
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = ‚mediacms.io‘
EMAIL_PORT = 587
ADMIN_EMAIL_LIST = [‚info@mediacms.io‘]
```

### 5.13 Onemogočite registracije uporabnikov iz določenih domen

Nastavite domene, ki niso veljavne za registracijo, prek te spremenljivke:

```
RESTRICTED_DOMAINS_FOR_USER_REGISTRATION = [
    ‚xxx.com‘, ‚emaildomainwhatever.com‘]
```

Alternativno lahko dovolite registracijo samo dovoljenim domenam. To je lahko koristno, če uporabljate mediacms kot
zasebno storitev znotraj organizacije in želite omogočiti brezplačno registracijo za člane organizacije, vendar zavrniti
registracijo iz vseh drugih domen. Nastavitev te možnosti prepove registracijo vseh domen, ki niso na seznamu. Privzeto
je prazen seznam, ki se ignorira. Za onemogočanje nastavite prazen seznam.

```
ALLOWED_DOMAINS_FOR_USER_REGISTRATION = [
    „private.com“,
    „vod.private.com“,
    „my.favorite.domain“,
    „test.private.com“]
```

### 5.14 Zahtevajte pregled s strani urednikov/upraviteljev/skrbnikov MediaCMS

```
MEDIA_IS_REVIEWED = False
```

Vsako naloženo medijsko datoteko je zdaj treba pregledati, preden se lahko prikaže v seznamu.
Uredniki/upravitelji/administratorji MediaCMS lahko obiščete stran medijev in jo uredite, kjer lahko vidite možnost, da
medij označite kot pregledan. Privzeto je to nastavljeno na True, tako da vsi mediji ne potrebujejo pregleda.

### 5.15 Določite največje število medijev za seznam predvajanja.

Nastavite drugačen prag na spremenljivki `MAX_MEDIA_PER_PLAYLIST`.

Primer:

```
MAX_MEDIA_PER_PLAYLIST = 14
```

### 5.16 Določite največjo velikost medijev, ki jih je mogoče naložiti

spremenite `UPLOAD_MAX_SIZE`.

privzeto je 4 GB

```
UPLOAD_MAX_SIZE = 800 * 1024 * 1000 * 5
```

### 5.17 Določite največjo velikost komentarjev

spremenite `MAX_CHARS_FOR_COMMENT`

privzeto:

```
MAX_CHARS_FOR_COMMENT = 10000
```

### 5.18 Koliko datotek lahko naložite hkrati

nastavite drugačen prag za `UPLOAD_MAX_FILES_NUMBER`
privzeto:

```
UPLOAD_MAX_FILES_NUMBER = 100
```

### 5.18 prisilite uporabnike, da potrdijo svoj e-poštni naslov ob registraciji

privzeta možnost za potrditev e-poštnega naslova je neobvezna. Nastavite to na obvezno, da prisilite uporabnike, da
potrdijo svoj e-poštni naslov, preden se lahko prijavijo

```
ACCOUNT_EMAIL_VERIFICATION = ‚optional‘
```

### 5.20 Omejitev števila poskusov prijave v račun

ko je doseženo to število

```
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 20
```

nastavi časovno omejitev (v sekundah)

```
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 5
```

### 5.21 Onemogoči registracijo uporabnikov

nastavi naslednjo spremenljivko na False

```
USERS_CAN_SELF_REGISTER = True
```

### 5.22 Konfiguriraj obvestila

Globalna obvestila, ki so implementirana, se nadzorujejo z naslednjimi možnostmi:

```
USERS_NOTIFICATIONS = {
    ‚MEDIA_ADDED‘: True,
}
```

Če želite onemogočiti obvestila za nove medije, nastavite na False.

Skrbniki prejemajo tudi obvestila o različnih dogodkih. Če želite onemogočiti obvestila, nastavite katero koli od
naslednjih možnosti na False.

```
ADMINS_NOTIFICATIONS = {
    ‚NEW_USER‘: True,
    ‚MEDIA_ADDED‘: True,
    ‚MEDIA_REPORTED‘: True,
}
```

- NEW_USER: dodan je nov uporabnik
- MEDIA_ADDED: dodan je medij
- MEDIA_REPORTED: poročilo za medij je bilo zadeto

### 5.23 Konfigurirajte dostop do medijev samo za člane

- Naredite delovni tok portala javnega, hkrati pa nastavite `GLOBAL_LOGIN_REQUIRED = True`, da lahko vsebino vidijo samo
  prijavljeni uporabniki.
- Če želite člane dodajati sami, lahko nastavite `REGISTER_ALLOWED = False` ali pa v `cms/settings.py` preverite
  možnosti v »django-allauth settings«, ki vplivajo na registracijo. Npr. nastavite portal samo za povabila ali pa
  nastavite potrditev e-pošte kot obvezno, tako da lahko nadzirate, kdo se registrira.

### 5.24 Omogočite zemljevid strani

Ali naj se omogoči ustvarjanje datoteke sitemap na http://your_installation/sitemap.xml (privzeto: False)

```
GENERATE_SITEMAP = False
```

### 5.25 Nadzor nad tem, kdo lahko dodaja komentarje

Privzeto `CAN_COMMENT = „all“` pomeni, da lahko vsi registrirani uporabniki dodajajo komentarje. Druge veljavne možnosti
so:

- **email_verified**, uporabnik mora ne le registrirati račun, ampak tudi potrditi e-poštni naslov (s klikom na
  povezavo, poslano ob registraciji). Očitno mora konfiguracija e-pošte delovati, sicer uporabniki ne bodo prejemali
  e-pošte.

- **advancedUser**, komentarje lahko dodajajo le uporabniki, ki so označeni kot napredni uporabniki. Upravitelji ali
  menedžerji MediaCMS lahko uporabnike naredijo za napredne uporabnike tako, da uredijo njihov profil in izberejo
  advancedUser.

### 5.26 Nadzor nad tem, ali lahko anonimni uporabniki prikažejo seznam vseh uporabnikov

Privzeto lahko anonimni uporabniki vidijo seznam vseh uporabnikov na platformi. Če želite to omejiti le na
avtentificirane uporabnike, nastavite:

```
ALLOW_ANONYMOUS_USER_LISTING = False
```

Ko je nastavljeno na False, bodo imeli dostop do API končne točke seznama uporabnikov le prijavljeni uporabniki.

### 5.27 Nadzor nad tem, kdo lahko vidi stran članov

Privzeto `CAN_SEE_MEMBERS_PAGE = „all“` pomeni, da lahko vsi registrirani uporabniki vidijo stran članov. Druge veljavne
možnosti so:

- **uredniki**, stran lahko vidijo samo uredniki MediaCMS
- **skrbniki**, stran lahko vidijo samo skrbniki MediaCMS

### 5.28 Zahtevajte odobritev uporabnika ob registraciji

Privzeto uporabniki ne potrebujejo odobritve, zato se lahko takoj po registraciji prijavijo (če je registracija odprta).
Če pa je parameter `USERS_NEEDS_TO_BE_APPROVED` nastavljen na `True`, morajo najprej pridobiti odobritev svojega računa
s strani administratorja, preden se lahko uspešno prijavijo.
Administratorji lahko odobrijo uporabnike na naslednje načine: 1. prek administracije Django, 2. prek strani za
upravljanje uporabnikov, 3. prek neposrednega urejanja strani profila. V vseh primerih nastavite »Is approved« na True.

## 6. Upravljanje strani

bo napisano

## 7. Nadzorna plošča Django

## 8. O delovnem toku portala

Kdo lahko objavlja vsebino, kako se vsebina prikaže na javnih seznamih. Razlika med statusi (zasebno, neobjavo, javno)

## 9. O vlogah uporabnikov

Razlike med upraviteljem MediaCMS, urednikom MediaCMS in prijavljenim uporabnikom

## 10. Dodajanje jezikov za napise in podnapise

za pisanje

## 11. Dodajanje/brisanje kategorij in oznak

Prek administrativnega dela - http://your_installation/admin/

## 12. Pretvorba videa

Dodajanje/brisanje ločljivosti in profilov s spreminjanjem baze podatkovne tabele `Encode profiles`
prek https://your_installation/admin/files/encodeprofile/

Na primer, stanje `Active` katerega koli profila lahko preklopite, da ga omogočite ali onemogočite.

## 13. Kako dodati statično stran v stranski vrstici

### 1. Ustvarite svojo html stran v templates/cms/

npr. podvojite in preimenujte about.html

```
sudo cp templates/cms/about.html templates/cms/volunteer.html
```

### 2. Ustvarite datoteko css v static/css/

```
touch static/css/volunteer.css
```

### 3. V datoteki html posodobite blok headermeta, da odraža vašo novo stran

```
{% block headermeta %}
<meta property="og:title" content="Volunteer - {{PORTAL_NAME}}">
<meta property="og:type" content="website">
<meta property="og:description" content="">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">
{
    „@context“: „https://schema.org“,
    „@type“: „BreadcrumbList“,
    „itemListElement“: [{
        „@type“: „ListItem“,
		„position“: 1,
        „name“: „{{PORTAL_NAME}}“,
        „item“: {
            „@type“: „WebPage“,
            „@id“: „{{FRONTEND_HOST}}“
        }
    },
    {
		„@type“: „ListItem“,
        „position“: 2,
        „name“: „Volunteer“,
        „item“: {
            „@type“: „VolunteerPage“,
            „@id“: „{{FRONTEND_HOST}}/volunteer“
        }
    }]
}
</script>
<link href="{% static "css/volunteer.css„ %}“ rel="stylesheet"/>
{% endblock headermeta %}
```

### 4. V datoteki html posodobite blok innercontent, da odraža vašo dejansko vsebino

Napišite, kar želite.

### 5. V datoteki css napišite ustrezne sloge za vašo datoteko html.

Napišite, kar želite.

### 6. Dodajte svoj pogled v datoteko files/views.py

```
def volunteer(request):
    „“„Pogled prostovoljca“„“
    context = {}
    return render(request, „cms/volunteer.html“, context)
```

### 7. Dodajte svoj vzorec URL-ja v datoteko files/urls.py

```
urlpatterns = [
    url(r„^$“, views.index),
    url(r„^about“, views.about, name="about"),
    url(r„^volunteer“, views.volunteer, name="volunteer"),
```

### 8. Dodajte svojo stran v levi stranski vrstici

Če želite dodati povezavo do svoje strani kot element menija v levi stranski vrstici,
dodajte naslednjo kodo za zadnjo vrstico v _commons.js

```
/* Checks that a given selector has loaded. */
const checkElement = async selector => {
    while ( document.querySelector(selector) === null) {
      await new Promise( resolve =>  requestAnimationFrame(resolve) )
    }
    return document.querySelector(selector);
  };

/* Checks that sidebar nav menu has loaded, then adds menu item. */
checkElement('.nav-menu')
.then((element) => {
     (function(){
        var a = document.createElement('a');
        a.href = "/volunteer";
        a.title = "Volunteer";

        var s = document.createElement('span');
        s.className = "menu-item-icon";

        var icon = document.createElement('i');
        icon.className = "material-icons";
        icon.setAttribute("data-icon", "people");

        s.appendChild(icon);
        a.appendChild(s);

        var linkText = document.createTextNode("Volunteer");
        var t = document.createElement('span');

        t.appendChild(linkText);
        a.appendChild(t);

        var listItem = document.createElement('li');
        listItem.className = "link-item";
        listItem.appendChild(a);

        //if signed out use 3rd nav-menu
        var elem = document.querySelector(".nav-menu:nth-child(3) nav ul");
        var loc = elem.innerText;
        if (loc.includes("About")){
          elem.insertBefore(listItem, elem.children[2]);
        } else { //if signed in use 4th nav-menu
          elem = document.querySelector(".nav-menu:nth-child(4) nav ul");
          elem.insertBefore(listItem, elem.children[2]);
        }
    })();
});
```

### 9. Ponovno zaženite spletni strežnik mediacms.

Na dockerju:

```
sudo docker stop mediacms_web_1 && sudo docker start mediacms_web_1
```

V nasprotnem primeru:

```
sudo systemctl restart mediacms
```

## 14. Dodajte Google Analytics.

Navodila prispeval @alberto98fx

1. Ustvarite datoteko:

``` touch $DIR/mediacms/templates/tracking.html ```

2. Dodajte skript Gtag/Analytics

3. V datoteki ``` $DIR/mediacms/templates/root.html``` boste videli datoteko, podobno tej:

```
<head>
    {% block head %}

        <title>{% block headtitle %}{{PORTAL_NAME}}{% endblock headtitle %}</title>

        {% include „common/head-meta.html“ %}

        {% block headermeta %}

        <meta property="og:title" content="{{PORTAL_NAME}}">
        <meta property="og:type" content="website">

        {%endblock headermeta %}

        {% block externallinks %}{% endblock externallinks %}

        {% include „common/head-links.html“ %}

        {% block topimports %}{%endblock topimports %}

        {% include „config/index.html“ %}

    {% endblock head %}

</head>
```

4. Dodajte  ``` {% include „tracking.html“ %} ``` na konec znotraj oddelka ```<head>```

5. Če uporabljate Docker in niste namestili celotnega imenika, morate povezati nov volumen:

```

    web:
    image: mediacms/mediacms:latest
    restart: unless-stopped
    ports:
      - „80:80“
    deploy:
      replicas: 1
    volumes:
      - ./templates/root.html:/home/mediacms.io/mediacms/templates/root.html
      - ./templates/tracking.html://home/mediacms.io/mediacms/templates/tracking.html

 ```

## 15. Odpravljanje težav z e-pošto

V poglavju [Konfiguracija](https://github.com/mediacms-io/mediacms/blob/main/docs/admins_docs.md#5-configuration) tega
priročnika smo videli, kako urediti nastavitve e-pošte.
Če še vedno ne moremo prejemati e-pošte iz MediaCMS, nam lahko naslednje pomaga odpraviti težavo – v večini primerov gre
za težavo z nastavitvijo pravega uporabniškega imena, gesla ali možnosti TLS.

Vnesite Django shell, na primer, če uporabljate namestitev Single Server:

```bash
source  /home/mediacms.io/bin/activate
python manage.py shell
```

in znotraj lupine

```bash
from django.core.mail import EmailMessage
from django.conf import settings

settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

email = EmailMessage(
    ‚title‘,
    ‚msg‘,
    settings.DEFAULT_FROM_EMAIL,
    [‚recipient@email.com‘],)

email.send(fail_silently=False)
```

Imate možnost, da prejmete e-pošto (v tem primeru bo poslana na recipient@email.com), sicer pa se bo prikazala napaka.
Na primer, če vnesem napačno geslo za svoj Gmail račun, se prikaže

```
SMTPAuthenticationError: (535, b'5.7.8 Uporabniško ime in geslo nista sprejeta. Več informacij najdete na\n5.7.8  https://support.google.com/mail/?p=BadCredentials d4sm12687785wrc.34 - gsmtp')
```

## 16. Pogosta vprašanja

Video se predvaja, vendar se za velike video datoteke ne prikažejo predogledne sličice

Verjetno je datoteka sprites ni bila ustvarjena pravilno.
Izhod funkcije files.tasks.produce_sprite_from_video() je v tem primeru podoben naslednjemu

```
convert-im6.q16: širina ali višina presega omejitev `/tmp/img001.jpg' @ error/cache.c/OpenPixelCache/3912.
```

Rešitev: uredite datoteko `/etc/ImageMagick-6/policy.xml` in nastavite večje vrednosti za vrstice, ki vsebujejo širino
in višino. Na primer

```
  <policy domain="resource" name="height" value="16000KP"/>
  <policy domain="resource" name="width" value="16000KP"/>
```

Novo dodane video datoteke bodo zdaj lahko ustvarile datoteko sprites, potrebno za predogled sličic. Da ponovno zaženete
to nalogo na obstoječih videih, vnesite Django shell

```
root@8433f923ccf5:/home/mediacms.io/mediacms# source  /home/mediacms.io/bin/activate
root@8433f923ccf5:/home/mediacms.io/mediacms# python manage.py shell
Python 3.8.14 (default, Sep 13 2022, 02:23:58)
```

in

```
In [1]: from files.models import Media
In [2]: from files.tasks import produce_sprite_from_video

In [3]: for media in Media.objects.filter(media_type='video', sprites=''):
   ...:     produce_sprite_from_video(media.friendly_token)
```

to bo ponovno ustvarilo sprite za videe, pri katerih je naloga spodletela.

## 17. Koda za soglasje s piškotki

V datoteki `templates/components/header.html` najdete preprosto kodo za soglasje s piškotki. Koda je komentirana, zato
morate odstraniti vrstici `{% comment %}` in `{% endcomment %}`, da jo omogočite. Ali pa lahko ta del nadomestite s
svojo kodo, ki obravnava pasice za soglasje s piškotki.

![Preprost kod za soglasje s piškotki](images/cookie_consent.png)

## 18. Onemogočite kodiranje in prikažite samo izvirno datoteko

Ko se videi naložijo, se kodirajo v več ločljivosti, kar je postopek, imenovan transkodiranje. Včasih to ni potrebno in
morate prikazati samo izvirno datoteko, npr. ko MediaCMS teče na strežniku z nizkimi zmogljivostmi. Da to dosežete,
uredite settings.py in nastavite

```
DO_NOT_TRANSCODE_VIDEO = True
```

To bo onemogočilo proces transkodiranja in prikazana bo samo originalna datoteka. Upoštevajte, da bo to onemogočilo tudi
ustvarjanje datotek sprites, tako da na predvajalniku videov ne boste imeli predoglednih sličic.

## 19. Zaobljeni koti na videih

Privzeto imajo predvajalnik videa in medijski elementi zdaj zaobljene kote na večjih zaslonih (ne na mobilnih). Če vam
ta sprememba ni všeč, nastavite `USE_ROUNDED_CORNERS = False` v `local_settings.py`.

## 20. Prevajanje

### 20.1 Nastavitev privzetega jezika

MediaCMS je privzeto na voljo v več jezikih. Da nastavite privzeti jezik, uredite datoteko `settings.py` in nastavite
LANGUAGE_CODE na kodo enega od jezikov.

### 20.2 Odstranite obstoječe jezike

Če želite omejiti število jezikov, ki so prikazani kot razpoložljivi, jih odstranite iz seznama LANGUAGES v
`settings.py` ali jih komentirajte. Prikazani so samo tisti, ki so tam.

### 20.3 Izboljšajte obstoječi prevod

Če želite izboljšati obstoječo prevedeno vsebino v jeziku, ki je že preveden, preverite jezik po imenu kode v
`files/frontend-translations/` in uredite ustrezno datoteko.

### 20.4 Dodajte več vsebine k obstoječemu prevodu

Vse besedilo ni prevedeno, zato lahko kadarkoli najdete manjkajoče nize, ki jih je treba dodati prevodu. Ideja je, da

a) besedilo naredite prevodljivo v kodi
b) dodate prevedeni niz

Za a) morate preveriti, ali se niz, ki ga želite prevesti, nahaja v imeniku frontend (aplikacija React) ali v predlogah
Django. Obstajajo primeri za oba.

1. predloge Django, ki se nahajajo v mapi templates/. Oglejte si `templates/cms/about.html`, da vidite primer, kako se
   to naredi
2. koda frontenda (React), oglejte si, kako se `translateString` uporablja v `frontend`

Ko je niz označen kot prevodljiv, ga najprej dodajte v `files/frontend-translations/en.py`, nato pa zaženite

```
python manage.py process_translations
```

, da se niz vnese v vse jezike. Če ta postopek ni upoštevan, PR ne bo sprejet. Niz ni treba prevajati v vse podprte
jezike, vendar je treba ukaz izvesti in obstoječe slovarje dopolniti z novimi nizi za vse jezike. S tem se zagotovi, da
v nobenem jeziku ne manjka noben niz, ki bi ga bilo treba prevesti.

Po izvedbi tega ukaza prevedite niz v želeni jezik. Če se niz, ki ga želite prevesti, nahaja v Django predlogah, vam ni
treba ponovno zgraditi frontenda. Če se sprememba nahaja v frontendu, boste morali ponovno zgraditi, da boste videli
spremembe. Pri tem vam lahko pomaga ukaz Makefile `make build-frontend`.

### 20.5 Dodajanje novega jezika in prevajanje

Za dodajanje novega jezika: dodajte jezik v settings.py, nato dodajte datoteko v `files/frontend-translations/`.
Prepričajte se, da kopirate začetne nize, tako da kopirate `files/frontend-translations/en.py` vanj.

## 21. Kako spremeniti video okvirje na videih

Med predvajanjem videa lahko po privzetem nastavitvah z miško preletite in si ogledate majhne slike, imenovane sprites,
ki so izvlečene vsakih 10 sekund videa. To število lahko spremenite na manjše, tako da izvedete naslednje:

* uredite ./frontend/src/static/js/components/media-viewer/VideoViewer/index.js in spremenite `seconds: 10 ` na želeno
  vrednost, npr. 2.
* uredite settings.py in nastavite isto število za vrednost SPRITE_NUM_SECS
* zdaj morate ponovno zgraditi frontend: najlažji način je zagnati `make build-frontend`, za kar potrebujete Docker

Po tem bodo na novo naloženi videi imeli sprites, ustvarjene z novim številom sekund.

## 22. Nadzor dostopa na podlagi vlog

Privzeto obstajajo 3 statusi za vse medije, ki se nahajajo v sistemu: javni, nezapisani, zasebni. Ko se doda podpora
RBAC, ima uporabnik, ki je del skupine, dostop do medijev, ki so objavljeni v eni ali več kategorijah, s katerimi je
skupina povezana. Potek dela je naslednji:

1. Ustvari se skupina.
2. Kategorija se poveže s skupino.
3. Uporabnik se doda v skupino.

Sedaj lahko uporabnik pregleduje medijske vsebine, tudi če so v zasebnem stanju. Uporabnik vidi tudi vse medijske
vsebine na strani kategorije.

Ko se uporabnik doda v skupino, se lahko nastavi kot član, sodelavec ali upravitelj.

- Član: uporabnik lahko pregleduje medije, ki so objavljeni v eni ali več kategorijah, s katerimi je ta skupina
  povezana.
- Sodelavec: poleg pregledovanja lahko uporabnik tudi ureja medije v kategoriji, povezani s to skupino. Lahko tudi
  objavlja medije v tej kategoriji.
- Upravitelj: zaenkrat enako kot sodelavec.

Primeri uporabe, ki jih omogoča RBAC:

- ogled medija v zasebnem stanju: če je RBAC omogočen, če je uporabnik član skupine, ki je povezana s kategorijo, in je
  medij objavljen v tej kategoriji, lahko uporabnik ogleda medij
- urejanje medija: če je RBAC omogočen in je uporabnik sodelavec v eni ali več kategorijah, lahko objavlja medije v teh
  kategorijah, če so povezani z eno skupino
- ogled vseh medijev kategorije: če je omogočen RBAC in uporabnik obišče kategorijo, lahko vidi seznam vseh medijev, ki
  so objavljeni v tej kategoriji, ne glede na njihovo stanje, pod pogojem, da je kategorija povezana s skupino, katere
  član je uporabnik
- ogled vseh kategorij, povezanih s skupinami, katere član je uporabnik: če je omogočen RBAC in uporabnik obišče seznam
  kategorij, lahko ogleda vse kategorije, ki so povezane s skupino, katere član je uporabnik

Kako omogočiti podporo RBAC:

```
USE_RBAC = True
```

v `local_settings.py` in ponovno zaženite primer.

## 23. Nastavitev SAML

Podprta je avtentikacija SAML, skupaj z možnostjo uporabe odgovora SAML in izvedbo koristnih dejanj, kot so nastavitev
vloge uporabnika v MediaCMS ali sodelovanje v skupinah.

Da omogočite podporo SAML, uredite local_settings.py in nastavite naslednje možnosti:

```
USE_RBAC = True
USE_SAML = True
USE_IDENTITY_PROVIDERS = True

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = (‚HTTP_X_FORWARDED_PROTO‘, ‚https‘)
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SOCIALACCOUNT_ADAPTER = ‚saml_auth.adapter.SAMLAccountAdapter‘
SOCIALACCOUNT_PROVIDERS = {
    „saml“: {
        „provider_class“: „saml_auth.custom.provider.CustomSAMLProvider“,
    }
}
```

Za nastavitev ponudnika SAML:

- Korak 1: Dodajte ponudnika identitete SAML

1. Prejdite na nadzorno ploščo
2. Izberite »Ponudnik identitete«
3. Konfigurirajte kot sledi:
    - **Ponudnik**: saml
    - **ID ponudnika**: ID za ponudnika
    - **IDP Config Name**: ime ponudnika
    - **Client ID**: identifikator, ki je del prijave in se deli z IDP.
    - **Site**: nastavite privzeto

- Korak 2: Dodajte konfiguracijo SAML
  Izberite zavihek SAML Configurations, ustvarite novo in nastavite:

1. **IDP ID**: Mora biti URL
2. **IDP certifikat**: x509cert od vašega ponudnika SAML
3. **SSO URL**:
4. **SLO URL**:
5. **URL metapodatkov SP**: URL metapodatkov, ki ga bo uporabil IDP. To je lahko https://{portal}/saml/metadata in ga
   samodejno ustvari MediaCMS

- Korak 3: Nastavite druge možnosti

1. **Nastavitve e-pošte**:
    - `verified_email`: Ko je omogočeno, bodo e-poštna sporočila iz odgovorov SAML označena kot preverjena.
    - `Odstrani iz skupin`: Ko je omogočeno, bo uporabnik po prijavi odstranjen iz skupine, če je bil odstranjen iz
      skupine na IDP.
2. **Globalno mapiranje vlog**: Mapira vlogo, ki jo vrne SAML (kot je nastavljeno v zavihku Konfiguracija SAML), z vlogo
   v MediaCMS.
3. **Mapiranje vlog v skupinah**: Mapira vlogo, ki jo vrne SAML (kot je nastavljeno v zavihku Konfiguracija SAML), z
   vlogo v skupinah, v katere bo uporabnik dodan.
4. **Mapiranje skupin**: To ustvari skupine, povezane s tem IDP. ID-ji skupin, kot prihajajo iz SAML, povezani s
   skupinami MediaCMS
5. **Povezovanje kategorij**: To povezuje ID skupine (iz odgovora SAML) s kategorijo v MediaCMS

Celotna namestitev SAML
z [vodnikom EntraID in koraki za odpravljanje težav je na voljo tukaj.](./saml_entraid_setup.md). Ta vodnik se lahko
uporabi kot referenca tudi za druge IDP.

## 24. Nastavitev ponudnikov identitete

Dodana je bila ločena aplikacija Django identity_providers, da se olajša številne konfiguracije, povezane z različnimi
ponudniki identitete. Če je ta omogočena, ponuja naslednje možnosti:

- omogoča dodajanje ponudnika identitete prek Django admin in nastavitev številnih preslikav, kot so preslikava skupin,
  preslikava globalnih vlog in drugo. Čeprav je SAML edini ponudnik, ki ga je mogoče dodati takoj, je mogoče z
  minimalnim naporom dodati katerega koli ponudnika identitete, ki ga podpira django allauth. Če odgovor ponudnika
  identitete vsebuje atribute, kot so vloga ali skupine, jih je mogoče preslikati na vloge (napreden uporabnik, urednik,
  upravitelj, administrator) in skupine (rbac skupine), specifične za MediaCMS.
- shrani dnevnike odgovorov SAML po avtentifikaciji uporabnika (lahko se uporabi tudi za druge ponudnike)
- omogoča določitev seznama možnosti prijave prek administratorja (npr. prijava v sistem, prijava ponudnika identitete)

da omogočite ponudnike identitete, nastavite naslednjo nastavitev v `local_settings.py`:

```
USE_IDENTITY_PROVIDERS = True
```

Ob obisku administratorja boste videli zavihek Ponudniki identitete, kjer lahko dodate enega.

## 25. Prilagojene URL-je

Da bi omogočili prilagojene URL-je, nastavite `ALLOW_CUSTOM_MEDIA_URLS = True` v settings.py ali local_settings.py.
To bo omogočilo urejanje URL-ja medija med urejanjem medija. Če je URL že zaseden, boste prejeli sporočilo, da ga ne
morete posodobiti.

## 26. Dovoljene datoteke

MediaCMS poskuša identificirati novo naložene datoteke in dovoli le določene vrste datotek, ki so navedene v nastavitvi
`ALLOWED_MEDIA_UPLOAD_TYPES`. Privzeto so dovoljene le datoteke [„video“, „audio“, ‚image‘, „pdf“].

Če datoteka ni identificirana kot ena od teh dovoljenih vrst, se datoteka odstrani iz sistema in se prikaže vnos, ki
kaže, da to ni podprta vrsta medija.

Če želite spremeniti dovoljene vrste datotek, uredite seznam `ALLOWED_MEDIA_UPLOAD_TYPES` v datoteki `settings.py` ali
`local_settings.py`. Če je v tem seznamu navedeno »vse«, se preverjanje ne izvede in so dovoljene vse datoteke.

## 27. Omejitve nalaganja za uporabnike

MediaCMS omogoča nastavitev največjega števila medijskih datotek, ki jih lahko naloži vsak uporabnik. To se nadzira z
nastavitvijo `NUMBER_OF_MEDIA_USER_CAN_UPLOAD` v `settings.py` ali `local_settings.py`. Privzeto je nastavljeno na 100
medijskih elementov na uporabnika.

Ko uporabnik doseže to omejitev, ne bo več mogel nalagati novih medijev, dokler ne izbriše nekaterih obstoječih vsebin.
Ta omejitev velja ne glede na vlogo ali dovoljenja uporabnika v sistemu.

Če želite spremeniti največje število dovoljenih nalaganj na uporabnika, spremenite vrednost
`NUMBER_OF_MEDIA_USER_CAN_UPLOAD` v datoteki z nastavitvami:

```
NUMBER_OF_MEDIA_USER_CAN_UPLOAD = 5
```

## 28. Whisper Transcribe za samodejne podnapise

MediaCMS se lahko integrira z OpenAI-jevim Whisperjem, da samodejno ustvari podnapise za vaše medijske datoteke. Ta
funkcija je koristna za boljšo dostopnost vaših vsebin.

### Kako deluje

Ko se za medijsko datoteko sproži naloga prepisovanja Whisper, MediaCMS za obdelavo avdio datoteke zažene ukazno orodje
`whisper` in ustvari datoteko s podnapisi v formatu VTT. Ustvarjeni podnapisi se nato povežejo z medijsko datoteko in so
na voljo pod možnostjo »avtomatski« jezik.

### Konfiguracija

Funkcija prepisovanja je na voljo samo za namestitev Docker. Da bi omogočili to funkcijo, morate uporabiti datoteko
`docker-compose.full.yaml`, saj vsebuje sliko z vsemi potrebnimi zahtevami, ali pa lahko nastavite, da storitev
celery_worker uporablja sliko mediacms:full namesto mediacms:latest. Nato morate v datoteki local_settings.py nastaviti
tudi: `USE_WHISPER_TRANSCRIBE = True`.

Privzeto imajo vsi uporabniki možnost poslati zahtevo za prepis videa, kot tudi za prepis in prevod v angleščino. Če
želite spremeniti to nastavitev, lahko uredite datoteko `settings.py` in nastavite `USER_CAN_TRANSCRIBE_VIDEO=False`.

Prepis privzeto uporablja osnovni model Whisper speech-to-text. Vendar lahko model spremenite z urejanjem nastavitve
`WHISPER_MODEL` v `settings.py`.
