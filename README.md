# Niño

This project follows [olc](https://mikacousin.github.io/olc) with better foundations.

## Building from git 

```bash
$ git clone https://github.com/mikacousin/nino.git
$ cd nino
$ meson builddir --prefix=/usr/local
$ sudo ninja -C builddir install
```

## data/fixtures/fixtures_ascii_to_json.py

This script extract fixtures templates from your Congo ASCII files to use them with Niño.
