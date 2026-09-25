"""Génère sitemap.xml à partir des pages du site et de data/data.json.
Usage : python scripts/generer_sitemap.py"""
import json
from pathlib import Path
from urllib.parse import quote

BASE = "https://quiditquoi2027.fr"
ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "data.json").read_text(encoding="utf-8"))
maj = D["majLe"]

pages = [("", "daily", "1.0"), ("programmes.html", "daily", "0.9"), ("candidats.html", "daily", "0.9"),
         ("declarations.html", "daily", "0.8"), ("comparateur.html", "daily", "0.8"), ("qui-a-dit-ca.html", "daily", "0.8"), ("quel-parti.html", "weekly", "0.8"),
         ("calendrier.html", "weekly", "0.6"), ("a-propos.html", "monthly", "0.3")]
urls = [(f"{BASE}/{p}", f, pr) for p, f, pr in pages]
urls += [(f"{BASE}/candidats/{quote(c['id'])}/", "daily", "0.8") for c in D["candidats"]]

out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, freq, prio in urls:
    loc = loc.replace("&", "&amp;")
    out.append(f"  <url><loc>{loc}</loc><lastmod>{maj}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority></url>")
out.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print(f"sitemap.xml : {len(urls)} URL")
