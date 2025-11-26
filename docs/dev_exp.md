# Izkušnje razvijalcev

Prizadevamo si za zagotavljanje boljših izkušenj razvijalcev in njihovo dokumentiranje.

## Kako razvijati lokalno z Dockerjem

Najprej namestite najnovejšo različico [Dockerja](https://docs.docker.com/get-docker/)
in [Docker Compose](https://docs.docker.com/compose/install/).

Nato zaženite `docker compose -f docker-compose-dev.yaml up`

```
user@user:~/mediacms$ docker compose -f docker-compose-dev.yaml up
```

V nekaj minutah bo aplikacija na voljo na http://localhost . Prijavite se z admin/admin

### Kaj počne docker-compose-dev.yaml?

Izgradi dve sliki, ki se uporabljata za backend in frontend.

* Backend: `mediacms/mediacms-dev:latest`
* Frontend: `frontend`

in zažene vse storitve, potrebne za MediaCMS, kot so Celery/Redis za asinhrone naloge, podatkovna baza PostgreSQL,
Django in React

Za Django so spremembe iz slike, ki jo je ustvaril docker-compose.yaml, naslednje:

* Django teče v načinu razhroščevanja z `python manage.py runserver`
* uwsgi in nginx ne tečeta
* Django teče v načinu razhroščevanja z orodno vrstico za razhroščevanje
* Statične datoteke (js/css) se naložijo iz mape static/
* corsheaders je nameščen in nastavljen tako, da dovoljuje vse izvore

Za React bo v mapi frontend izvedel `npm start`, kar bo zagnal razvojni strežnik.
Preverite na http://localhost:8088/

### Kako razvijati v Djangu

Django se zažene na http://localhost in se samodejno ponovno nalaga. Vsaka sprememba v kodi python naj bi osvežila
Django.

Če Django zaradi napake (npr. SyntaxError, med urejanjem) preneha delovati ga je potrebno ponovno zagnati

```
docker compose -f docker-compose-dev.yaml restart web
```

### Kako razvijati v React

React se zažene na http://localhost:8088/ , koda se nahaja v frontend/ , zato naj bi spremembe tam imele takojšen učinek
na stran. Upoštevajte, da React nalaga podatke iz Django in da mora biti zgrajen tako, da ga Django lahko uporablja.

### Spremembe v frontendu

Način dodajanja Reacta je bolj zapleten kot pri običajnem projektu SPA, saj se React uporablja kot knjižnica, ki jo
naloži Django Templates, zato ni samostojen projekt in ne obdeluje poti itd.

Upoštevati je treba dve mapi:

* frontend/src za datoteke Reacta
* templates/ za predloge Django.

Django uporablja zelo intuitiven hierarhični sistem predlog (https://docs.djangoproject.com/en/4.2/ref/templates/), kjer
je osnovna predloga templates/root.html, vse druge predloge pa jo razširjajo.

React se pokliče prek Django predlog, npr. templates/cms/media.html naloži js/media.js

Da bi spremenili kodo React, uredite kodo v frontend/src in preverite njen učinek na http://localhost:8088/ . Ko je
pripravljeno, ga zgradite in kopirajte v statično mapo Django, da ga Django lahko uporablja.

### Razvojni delovni tok s frontendom

1. Uredi datoteke frontend/src/
2. Preveri spremembe na http://localhost:8088/
3. Zgradi frontend z `docker compose -f docker-compose-dev.yaml exec frontend npm run dist`
4. Kopirajte statične datoteke v statično mapo Django z `cp -r frontend/dist/static/* static/`.
5. Ponovno zaženite Django – `docker compose -f docker-compose-dev.yaml restart web`, da bo uporabljal nove statične
   datoteke.
6. Potrdite spremembe.

### Pomožni ukazi

Prizadevamo si zagotoviti pomožne ukaze, v Makefile preverite, kaj podpira. Npr.

Bash v spletni kontejner:

```
user@user:~/mediacms$ make admin-shell
root@ca8c1096726b:/home/mediacms.io/mediacms# ./manage.py shell
```

Zgradite frontend:

```
user@user:~/mediacms$ make build-frontend
docker compose -f docker-compose-dev.yaml exec frontend npm run dist

> mediacms-frontend@0.9.1 dist /home/mediacms.io/mediacms/frontend
> mediacms-scripts rimraf ./dist && mediacms-scripts build --config=./config/mediacms.config.js --env=dist
```
