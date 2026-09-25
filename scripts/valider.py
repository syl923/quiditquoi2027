"""Vérifie data/data.json avant publication. Usage : python scripts/valider.py
Code de sortie 0 = OK, 1 = erreurs (ne pas publier)."""
import json, re, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "data.json"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUTS = {"declare", "primaire", "pressenti", "retire"}
errs = []

def err(msg):
    errs.append(msg)

try:
    D = json.loads(DATA.read_text(encoding="utf-8"))
except Exception as e:
    print(f"JSON invalide : {e}")
    sys.exit(1)

for k in ["majLe", "sources", "election", "themes", "syntheses", "candidats", "declarations", "positions", "calendrier"]:
    if k not in D:
        err(f"clé manquante : {k}")
if errs:
    print("\n".join(errs)); sys.exit(1)

sources = D["sources"]
for key, s in sources.items():
    if not s.get("titre") or not str(s.get("url", "")).startswith(("https://", "http://")):
        err(f"source {key} : titre ou url invalide")

def check_source(where, x):
    if x.get("source") not in sources:
        err(f"{where} : source '{x.get('source')}' absente de 'sources'")

def check_date(where, v):
    if not isinstance(v, str) or not DATE.match(v):
        err(f"{where} : date invalide '{v}' (attendu AAAA-MM-JJ)")

check_date("majLe", D["majLe"])
check_date("election.premierTour", D["election"].get("premierTour"))
check_date("election.secondTour", D["election"].get("secondTour"))

themes = {t["id"] for t in D["themes"]}
cands = set()
for c in D["candidats"]:
    w = f"candidat {c.get('id')}"
    for f in ["id", "nom", "parti", "couleur", "statut", "bio"]:
        if not c.get(f):
            err(f"{w} : champ '{f}' manquant")
    if c.get("id") in cands:
        err(f"{w} : id en double")
    cands.add(c.get("id"))
    if c.get("statut") not in STATUTS:
        err(f"{w} : statut '{c.get('statut')}' inconnu")
    if not re.match(r"^#[0-9a-fA-F]{6}$", str(c.get("couleur"))):
        err(f"{w} : couleur invalide")
    if "dateDeclaration" in c:
        check_date(w, c["dateDeclaration"])
    check_source(w, c)
    if "photo" in c:
        ph = c["photo"]
        if not (ph.get("fichier") and ph.get("credit") and ph.get("url")):
            err(f"{w} : photo incomplète (fichier, credit, url)")
        elif not (DATA.parent.parent / ph["fichier"]).is_file():
            err(f"{w} : fichier photo introuvable {ph['fichier']}")

seen = set()
for i, d in enumerate(D["declarations"]):
    w = f"declaration #{i} ({d.get('candidat')})"
    if d.get("candidat") not in cands: err(f"{w} : candidat inconnu")
    if d.get("theme") not in themes: err(f"{w} : thème inconnu")
    if not d.get("texte"): err(f"{w} : texte vide")
    check_date(w, d.get("date"))
    check_source(w, d)
    key = (d.get("candidat"), d.get("texte"))
    if key in seen: err(f"{w} : déclaration en double")
    seen.add(key)

for i, p in enumerate(D["positions"]):
    w = f"position #{i} ({p.get('candidat')}/{p.get('theme')})"
    if p.get("candidat") not in cands: err(f"{w} : candidat inconnu")
    if p.get("theme") not in themes: err(f"{w} : thème inconnu")
    if not p.get("resume"): err(f"{w} : résumé vide")
    check_source(w, p)

for i, e in enumerate(D["calendrier"]):
    w = f"calendrier #{i}"
    check_date(w, e.get("date"))
    if not e.get("titre"): err(f"{w} : titre vide")
    if "source" in e: check_source(w, e)

QUIZ = DATA.parent / "quiz-partis.json"
if QUIZ.exists():
    try:
        Q = json.loads(QUIZ.read_text(encoding="utf-8"))
        if len(Q["questions"]) > 20: err(f"quiz : {len(Q['questions'])} questions (20 au maximum)")
        ids = [q["id"] for q in Q["questions"]]
        for i in set(ids):
            if ids.count(i) > 1: err(f"quiz : id de question en double {i}")
        for q in Q["questions"]:
            if not q.get("question"): err(f"quiz {q['id']} : question vide")
            if not 3 <= len(q["options"]) <= 5: err(f"quiz {q['id']} : {len(q['options'])} réponses (3 à 5 attendues)")
            for o in q["options"]:
                if not o.get("texte"): err(f"quiz {q['id']} : réponse vide")
                for cid in o["candidats"]:
                    if cid not in cands: err(f"quiz {q['id']} : candidat inconnu {cid}")
                for k in o["sources"]:
                    if k not in sources: err(f"quiz {q['id']} : source inconnue {k}")
                if o["candidats"] and not o["sources"]: err(f"quiz {q['id']} : réponse sans source")
    except Exception as e:
        err(f"quiz-partis.json invalide : {e}")

if errs:
    print(f"{len(errs)} erreur(s) :")
    print("\n".join(" - " + e for e in errs))
    sys.exit(1)
print(f"OK : {len(D['candidats'])} candidats, {len(D['declarations'])} déclarations, {len(D['positions'])} positions, {len(sources)} sources.")
