#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Fangschuß",
    "--doc-subtitle", "Notizen aus der U-Haft",
    # "--doc-subject", "",
    "--doc-date", "2026-07-07",
    "--doc-edition", "1",
    "--doc-extent", "272 pages",
    "--color-image-pages", "273,274",
    "--doc-author", "Kurt Hättasch",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "Verlag Antaios",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9783949041235",
    "--doc-cover-image", "0663-level/273.tiff",
    "--canonical-url-base", "https://milahu.github.io/kurt-haettasch-fangschuss-2026/",
    "--doc-description", """
Kurt Hättasch, Jahrgang 1999, sitzt seit dem 5. November 2024 in U-Haft.
Man wirft ihm die Beteiligung an der Bildung einer terroristischen Vereinigung vor.
Die Polizei schoß Hättasch nieder, als sie ihn festnehmen wollte.

Hättasch beschreibt in seinen Notizen nicht nur diesen Tag,
sondern den Alltag einer Haft, von der er nicht weiß, wann sie zuende sein wird.

Unterbrochen wird die Monotonie durch Tage voller Hoffnung auf Haftentlassung und auf einen beherzten Richter,
der nicht zuschaut, wie jemand um seine Lebenszeit gebracht wird.

Hättasch ist Familienvater, Handwerksmeister, Stimmführer am Flügelhorn,
Dozent an der Handwerkskammer, Absolvent der Offizierschule des Heeres und Jäger.
Er war Schatzmeister der Jungen Alternative Sachsen und saß für die AfD als Fraktionschef im Stadtrat Grimma.

Alles Fassade?
Dahinter soll sich ein Umsturz vorbereitet haben?
Selbst Mainstream-Journalisten sagen,
daß die Indizienlage zu dünn ist für einen solchen Verdacht.

Warum veröffentlicht Antaios Hättaschs Notizen aus der U-Haft?

1. Wir sind nach Gesprächen und Sondierungen überzeugt davon,
daß der Verdacht nicht bestätigt werden kann
und halten den Prozeß für einen politischen Prozeß.
2. Wir kennen Hättasch und seine Frau,
nahmen ihn auf Veranstaltungen als besonnen und heimatverbunden wahr
und glauben seiner Version der Geschichte.
3. Wir sind der Überzeugung,
daß aller parteipolitischer Erfolg nicht dazu führen darf,
diejenigen zu vergessen, an denen ein Exempel statuiert werden soll.
4. Es geht vor allem um Solidarität mit einer jungen Familie.
Sie ist unter anderem durch finanzielle Unterstützung möglich:
Der Erlös aus dem Verkauf dieses Hafttagebuchs geht an Familie Hättasch und dient zur Finanzierung der Verteidigung.

Das Nachwort hat Anwalt Dubravko Mandic beigesteuert.
Er beschreibt die Struktur politischer Prozesse und juristischer Zermürbung.
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
