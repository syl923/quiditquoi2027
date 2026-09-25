"""Télécharge une photo sous licence libre (Wikimedia Commons) pour chaque candidat sans photo.
Usage : python scripts/photos.py            (candidats sans photo)
        python scripts/photos.py --verifier (liste seulement, ne modifie rien)
Les photos vont dans assets/photos/<id>.jpg ; data/data.json reçoit le champ "photo"."""
import json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "data.json"
OUT = ROOT / "assets" / "photos"
UA = {"User-Agent": "quiditquoi2027-bot/1.0 (https://quiditquoi2027.fr; loc.narsau@gmail.com)"}
LIBRES = re.compile(r"^(CC0|CC BY(-SA)? [0-9.]+( [A-Za-z]+)?|Public domain|Domaine public|PD|Attribution|CC BY [0-9.]+|CC-BY[\w.-]*|Licence Ouverte.*|Etalab.*)", re.I)

def api(host, params):
    url = f"https://{host}/w/api.php?" + urllib.parse.urlencode({**params, "format": "json", "formatversion": 2})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)

def texte(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()

def photo_pour(nom):
    q = api("fr.wikipedia.org", {"action": "query", "titles": nom, "prop": "pageimages", "piprop": "name", "redirects": 1})
    page = q["query"]["pages"][0]
    fichier = page.get("pageimage")
    if not fichier:
        return None, "pas d'image principale sur Wikipédia"
    q = api("commons.wikimedia.org", {"action": "query", "titles": "File:" + fichier, "prop": "imageinfo",
                                       "iiprop": "url|extmetadata", "iiurlwidth": 400})
    pages = q["query"]["pages"]
    if not pages or "imageinfo" not in pages[0]:
        return None, "image absente de Commons (probablement non libre)"
    ii = pages[0]["imageinfo"][0]
    meta = ii.get("extmetadata", {})
    licence = texte(meta.get("LicenseShortName", {}).get("value"))
    if not LIBRES.match(licence):
        return None, f"licence non reconnue comme libre : {licence!r}"
    auteur = texte(meta.get("Artist", {}).get("value")) or "Auteur inconnu"
    return {"thumb": ii["thumburl"], "credit": f"{auteur[:80]} — {licence}", "url": ii["descriptionurl"]}, None

def main():
    verif = "--verifier" in sys.argv
    D = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    lignes = DATA.read_text(encoding="utf-8").split("\n")
    change = 0
    for c in D["candidats"]:
        if c.get("photo"):
            continue
        info, err = photo_pour(c["nom"])
        if err:
            print(f"- {c['nom']} : {err}")
            continue
        print(f"+ {c['nom']} : {info['credit']}")
        if verif:
            continue
        dest = OUT / f"{c['id']}.jpg"
        with urllib.request.urlopen(urllib.request.Request(info["thumb"], headers=UA), timeout=60) as r:
            dest.write_bytes(r.read())
        photo = {"fichier": f"assets/photos/{c['id']}.jpg", "credit": info["credit"], "url": info["url"]}
        # Remplace la ligne du candidat en gardant le format « un objet par ligne ».
        for i, l in enumerate(lignes):
            if l.strip().startswith('{"id":"%s"' % c["id"]):
                obj = json.loads(l.strip().rstrip(","))
                obj["photo"] = photo
                lignes[i] = l[: len(l) - len(l.lstrip())] + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ("," if l.rstrip().endswith(",") else "")
                change += 1
    if change:
        DATA.write_text("\n".join(lignes), encoding="utf-8", newline="\n")
    print(f"{change} photo(s) ajoutée(s).")

main()
