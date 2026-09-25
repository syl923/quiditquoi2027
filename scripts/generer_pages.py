"""Génère une page HTML statique par candidat : candidats/<id>/index.html.
Ces pages sont lisibles par Google sans JavaScript (le JS n'ajoute que l'en-tête et le pied de page).
Usage : python scripts/generer_pages.py"""
import json, shutil
from html import escape
from pathlib import Path

BASE = "https://quiditquoi2027.fr"
ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "data.json").read_text(encoding="utf-8"))
OUT = ROOT / "candidats"

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
STATUTS = {"declare": "Candidature déclarée", "primaire": "En primaire", "pressenti": "Pressenti", "retire": "Retiré"}
THEMES = {t["id"]: t for t in D["themes"]}
SOURCES = D["sources"]


def e(s):
    return escape(str(s or ""), quote=True)


def date_fr(iso):
    a, m, j = iso.split("-")
    return f"{int(j)}{'er' if j == '01' else ''} {MOIS[int(m) - 1]} {a}"


def initiales(nom):
    return "".join(p[0] for p in nom.split()[:2]).upper()


def avatar(c, cls=""):
    inner = f'<img src="/{e(c["photo"]["fichier"])}" alt="{e(c["nom"])}">' if c.get("photo") else e(initiales(c["nom"]))
    return f'<div class="avatar {cls}" style="--c:{e(c["couleur"])}">{inner}</div>'


def lien_source(cle):
    s = SOURCES.get(cle, {"titre": "Source", "url": "#"})
    return f'<a class="source-link" href="{e(s["url"])}" target="_blank" rel="noopener nofollow">Source : {e(s["titre"])} ↗</a>'


def page(c):
    pos = [p for p in D["positions"] if p["candidat"] == c["id"]]
    decls = sorted((d for d in D["declarations"] if d["candidat"] == c["id"]), key=lambda d: d["date"], reverse=True)
    url = f"{BASE}/candidats/{c['id']}/"
    titre = f"{c['nom']} 2027 : programme, déclarations et positions"
    themes_txt = ", ".join(THEMES[t]["nom"].lower() for t in dict.fromkeys(p["theme"] for p in pos) if t in THEMES)
    desc = f"{c['nom']} ({c['parti']}) et la présidentielle 2027 : {STATUTS.get(c['statut'], '').lower()}, déclarations sourcées"
    desc += f" et propositions ({themes_txt})." if themes_txt else "."
    image = f"{BASE}/{c['photo']['fichier']}" if c.get("photo") else f"{BASE}/assets/og.png"
    jsonld = {
        "@context": "https://schema.org", "@type": "ProfilePage",
        "mainEntity": {"@type": "Person", "name": c["nom"], "affiliation": c["parti"], "description": c["bio"],
                        **({"image": image} if c.get("photo") else {})},
        "url": url, "dateModified": D["majLe"], "inLanguage": "fr-FR",
    }

    # Positions groupées par thème, dans l'ordre des thèmes du site.
    blocs_pos = []
    for tid, t in THEMES.items():
        ps = [p for p in pos if p["theme"] == tid]
        if not ps:
            continue
        items = "".join(f"<li>{e(p['resume'])}<br>{lien_source(p['source'])}</li>" for p in ps)
        blocs_pos.append(f'<div class="card pos-card" style="--c:{e(c["couleur"])}"><h3 style="margin-top:0">{t["emoji"]} {e(t["nom"])}</h3><ul class="pos-list">{items}</ul></div>')
    pos_html = f'<div class="grid">{"".join(blocs_pos)}</div>' if blocs_pos else '<p class="empty">Aucune position sourcée pour l\'instant.</p>'

    decl_html = "".join(f"""
      <article class="card decl" style="--c:{e(c['couleur'])}">
        <div class="decl-meta">{date_fr(d['date'])}{' · ' + e(d.get('contexte')) if d.get('contexte') else ''}</div>
        <blockquote>{e(d['texte'])}</blockquote>
        <div class="decl-foot">
          <div class="badges" style="margin:0">{f'<span class="badge">{THEMES[d["theme"]]["emoji"]} {e(THEMES[d["theme"]]["nom"])}</span>' if d["theme"] in THEMES else ''}</div>
          {lien_source(d['source'])}
        </div>
      </article>""" for d in decls) or '<p class="empty">Aucune déclaration pour l\'instant.</p>'

    autres = [o for o in D["candidats"] if o["id"] != c["id"] and o["statut"] in ("declare", "primaire")]
    autres_html = "".join(f'<a href="/candidats/{e(o["id"])}/">{avatar(o)}{e(o["nom"])}</a>' for o in autres)

    credit = ""
    if c.get("photo"):
        credit = f'<p class="photo-credit">Photo : <a href="{e(c["photo"]["url"])}" target="_blank" rel="noopener">{e(c["photo"]["credit"])}</a>, via Wikimedia Commons</p>'

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titre)} — Qui dit quoi 2027</title>
  <meta name="description" content="{e(desc)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/style.css">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="profile">
  <meta property="og:site_name" content="Qui dit quoi 2027">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:title" content="{e(titre)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{e(image)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#6d28d9">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" type="image/png" href="/assets/icon-512.png">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body data-page="fiche">
  <div id="site-header"></div>

  <main class="container">
    <nav class="fiche-nav" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="/candidats.html">Candidats</a> › {e(c['nom'])}</nav>

    <div class="profile" style="--c:{e(c['couleur'])}">
      {avatar(c, "lg")}
      <div>
        <h1>{e(c['nom'])}</h1>
        <div class="parti">{e(c['parti'])}</div>
        <div class="badges">
          <span class="badge {e(c['statut'])}">{STATUTS.get(c['statut'], e(c['statut']))}</span>
          {f'<span class="badge">Déclaré le {date_fr(c["dateDeclaration"])}</span>' if c.get('dateDeclaration') else ''}
        </div>
      </div>
    </div>
    <p class="page-intro">{e(c['bio'])}<br>{lien_source(c['source'])}</p>
    {credit}

    <section class="section">
      <div class="section-head"><h2>Le programme de {e(c['nom'])} par thème</h2><a href="/comparateur.html">Comparer →</a></div>
      {pos_html}
    </section>

    <section class="section">
      <div class="section-head"><h2>Les déclarations de {e(c['nom'])}</h2></div>
      <div class="list">{decl_html}
      </div>
    </section>

    <section class="section">
      <div class="section-head"><h2>Les autres candidats</h2><a href="/candidats.html">Tous →</a></div>
      <div class="autres">{autres_html}</div>
    </section>

    <p class="decl-meta">Fiche mise à jour le {date_fr(D['majLe'])}. Une erreur ? <a href="/a-propos.html#contact">Signalez-la</a>.</p>
  </main>

  <div id="site-footer"></div>
  <script src="/assets/app.js"></script>
  <script data-goatcounter="https://quiditquoi2027.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for c in D["candidats"]:
        d = OUT / c["id"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(page(c), encoding="utf-8", newline="\n")
    print(f"{len(D['candidats'])} pages candidats générées dans candidats/")


main()
