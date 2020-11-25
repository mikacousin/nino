# Niño

[French](README.fr.md)

This project follows [olc](https://mikacousin.github.io/olc) with better foundations.

Tested on Archlinux and Windows 10 (with [MSYS2](https://www.msys2.org)).

## Building from git

```bash
$ git clone https://github.com/mikacousin/nino.git
$ cd nino
$ meson builddir --prefix=/usr/local
$ sudo ninja -C builddir install
```

## fixtures_ascii_to_json.py

This script extract fixtures templates from your Congo ASCII files and generate json files used by Niño.

To get help:

```bash
$ cd data/fixtures
$ ./fixtures_ascii_to_json.py --help
```
