# Dovoljenja za medije v MediaCMS

Ta dokument pojasnjuje sistem dovoljenj v MediaCMS, ki nadzira, kdo lahko pregleduje, ureja in upravlja medijske datoteke.

## Pregled

MediaCMS ponuja prilagodljiv sistem dovoljenj, ki omogoča natančen nadzor nad dostopom do medijev. Sistem podpira:

1. **Osnovna dovoljenja** – javne, zasebne in neobjave medijske datoteke
2. **Dovoljenja za posamezne uporabnike** – neposredna dovoljenja, dodeljena posameznim uporabnikom
3. **Nadzor dostopa na podlagi vlog (RBAC)** – dovoljenja na podlagi kategorij prek članstva v skupini

## Stanja medijskih datotek

Vsaka medijska datoteka ima stanje, ki določa njeno osnovno vidnost:

- **Javno** – vidno vsem
- **Zasebna** – vidna samo lastniku in uporabnikom z izrecnimi dovoljenji
- **Nenavedeni** – niso navedeni v javnih seznamih, vendar so dostopni prek neposredne povezave

## Vloge uporabnikov

MediaCMS ima več vlog uporabnikov, ki vplivajo na dovoljenja:

- **Običajni uporabnik** – lahko nalaga in upravlja svoje lastne medijske datoteke
- **Napreden uporabnik** – dodatne zmogljivosti (konfigurativne)
- **Urednik MediaCMS** – lahko ureja in pregleduje vsebino na platformi
- **Upravitelj MediaCMS** – polne upravljavske zmogljivosti
- **Skrbnik** – popoln dostop do sistema

## Neposredna dovoljenja za medije

Model `MediaPermission` omogoča dodeljevanje posebnih dovoljenj posameznim uporabnikom:

### Ravni dovoljenj

- **Gledalec** – lahko si ogleda medije, tudi če so zasebni
- **Urednik** – lahko si ogleda in ureja metapodatke medijev
- **Lastnik** – popoln nadzor, vključno z brisanjem

## Nadzor dostopa na podlagi vlog (RBAC)

Ko je omogočen RBAC (nastavitev `USE_RBAC`), je mogoče dovoljenja upravljati prek kategorij in skupin:

1. Kategorije je mogoče označiti kot nadzorovane z RBAC.
2. Uporabniki so dodeljeni skupinam RBAC z določenimi vlogami.
3. Skupine RBAC so povezane s kategorijami.
4. Uporabniki podedujejo dovoljenja za medije v teh kategorijah na podlagi svoje vloge.

### Vloge RBAC

- **Član** – lahko pregleduje medije v kategoriji.
- **Sodelavec** – lahko pregleduje in ureja medije v kategoriji.
- **Upravitelj** – ima popoln nadzor nad mediji v kategoriji.

## Metode preverjanja dovoljenj

Model uporabnika ponuja več metod za preverjanje dovoljenj:

```python
# Iz users/models.py
def has_member_access_to_media(self, media):
    # Preveri, ali lahko uporabnik pregleduje medijske vsebine.
    # ...

def has_contributor_access_to_media(self, media):
    # Preveri, ali lahko uporabnik ureja medijske vsebine.
    # ...

def has_owner_access_to_media(self, media):
    # Preveri, ali ima uporabnik popoln nadzor nad mediji
    # ...
```

## Kako se uporabljajo dovoljenja

Ko uporabnik poskuša dostopati do medijev, sistem preveri dovoljenja v naslednjem vrstnem redu:

1. Ali so mediji javni? Če da, dovoli dostop.
2. Ali je uporabnik lastnik medijev? Če da, dovoli popoln dostop.
3. Ali ima uporabnik neposredna dovoljenja prek MediaPermission? Če da, dodeli ustrezno raven dostopa.
4. Če je omogočen RBAC, ali ima uporabnik dostop prek članstva v kategoriji? Če da, dodeli ustrezno raven dostopa.
5. Če ni nobena od zgoraj navedenih možnosti, zavrni dostop.

## Deljenje medijev

Uporabniki lahko medije delijo z drugimi tako, da:

1. jih naredijo javne ali nezapisane
2. dodelijo neposredna dovoljenja določenim uporabnikom
3. jih dodajo v kategorijo, ki je dostopna skupini RBAC

## Podrobnosti izvedbe

### Seznam medijev

Pri navajanju medijev sistem filtrira na podlagi dovoljenj:

```python
# Poenostavljen primer iz datotek/pogledov/media.py
def _get_media_queryset(self, request, user=None):
    # 1. Javni mediji
    listable_media = Media.objects.filter (listable=True)

    if not request.user.is_authenticated:
        return listable_media

    # 2. Uporabniška dovoljenja za avtenticirane uporabnike
    user_media = Media.objects.filter(permissions__user=request.user)

    # 3. RBAC za avtenticirane uporabnike
    if getattr(settings, ‚USE_RBAC‘, False):
        rbac_categories = request.user.get_rbac_categories_as_member()
        rbac_media = Media.objects.filter(category__in=rbac_categories)

    # Kombiniraj vse dostopne medije
    return listable_media.union(user_media, rbac_media)
```

### Preverjanje dovoljenj

Sistem uporablja pomožne metode za preverjanje dovoljenj:

```python
# Iz users/models.py
def has_member_access_to_media(self, media):
    # Najprej preveri, ali je uporabnik lastnik
    if media.user == self:
        return True

    # Nato preveri dovoljenja RBAC
    if getattr(settings, ‚USE_RBAC‘, False):
        rbac_groups = RBACGroup.objects.filter(
            memberships__user=self,
            memberships__role__in=["member", "contributor", "manager"],
            categories__in=media.category.all()
        ).distinct()
        if rbac_groups.exists():
            return True

    # Nato preveri dovoljenja MediaShare za kakršen koli dostop
    media_permission_exists = MediaPermission.objects.filter(
        user=self,
        media=media,
    ).exists()

    return media_permission_exists
```

## Najboljše prakse

1. **Privzeto zasebno** – razmislite o nastavitvi novih naložb kot privzeto zasebnih.
2. **Uporabite kategorije** – medije razvrstite v kategorije za lažje upravljanje dovoljenj.
3. **RBAC za ekipe** – uporabite RBAC za scenarije sodelovanja v ekipi.
4. **Neposredna dovoljenja za izjeme** – uporabite neposredna dovoljenja za enkratno deljenje.

## Konfiguracija

Sistem dovoljenj lahko konfigurirate z več nastavitvami:

- `USE_RBAC` – omogoči/onemogoči nadzor dostopa na podlagi vlog.
