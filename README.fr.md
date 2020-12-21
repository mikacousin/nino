# niño

Ce programme fait suite à [olc](https://mikacousin.github.io/olc) avec de meilleurs fondations.

Son but est de fournir une console lumière libre et moderne. En comparant aux produits ETC, il est entre Cobalt et EOS. Il gère les intensitées comme Cobalt (vous devez indiquer les niveaux à chaque mémoire) et tous les autres paramètres comme EOS (une valeur reste en place tant qu'on ne la modifie pas).

Il est testé sous Archlinux et Windows 10 (avec [MSYS2](https://www.msys2.org)).

## Construction à partir de git

```bash
$ git clone https://github.com/mikacousin/nino.git
$ cd nino
$ meson builddir --prefix=/usr/local
$ sudo ninja -C builddir install
```

## fixtures_ascii_to_json.py

Ce script extrait les modèles de projecteurs asservis de vos fichiers Cobalt/Congo (ASCII) et génère des fichiers json utilisés par niño.

### Utilisation:

```bash
$ cd data/fixtures
$ ./fixtures_ascii_to_json.py --file fichier.asc
```
