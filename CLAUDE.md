# Qui dit quoi 2027 — contexte pour Claude

Site statique, neutre et sourcé sur l'élection présidentielle française de 2027 (1er tour 18 avril 2027, 2nd tour 2 mai 2027).
En ligne sur https://quiditquoi2027.fr (Netlify ; chaque push sur `main` est publié en quelques secondes).
Le propriétaire est un particulier anonyme (contact : loc.narsau@gmail.com). Il parle français : réponds en français, simplement.

## Architecture

- HTML/CSS/JS sans framework ni build. Pas de Node : les scripts sont en Python (bibliothèque standard ; Pillow seulement pour les images).
- Toutes les données sont dans `data/data.json` (sources, candidats, déclarations, positions, synthèses, calendrier). Les autres fichiers y font référence par des clés (`source`, `candidat`, `theme`).
- `assets/app.js` charge `/data/data.json` et affiche les pages dynamiques ; il gère aussi l'en-tête et le pied de page de toutes les pages.
- `candidats/<id>/index.html` : fiches candidats **générées** par `scripts/generer_pages.py`. Ne jamais les modifier à la main.
- `data/quiz-partis.json` : questions du quiz « Quel parti vous correspond ? » (chaque réponse renvoie aux candidats/partis dont la position est sourcée dans `data.json`).
- `_redirects` : redirections Netlify (ancien domaine netlify.app, www, anciennes fiches `candidat.html?id=`).

## Commandes (à lancer après toute modification des données)

```
python scripts/valider.py          # contrôle de cohérence : doit afficher OK avant tout push
python scripts/photos.py           # photos libres (Wikimedia Commons) pour les candidats sans photo
python scripts/generer_pages.py    # régénère candidats/<id>/
python scripts/generer_sitemap.py  # régénère sitemap.xml
```
Aperçu local : `python -m http.server 8027` puis http://localhost:8027 (ouvrir les fichiers directement ne charge pas les données).

## Règles éditoriales (non négociables)

1. Aucune information sans source d'un média identifiable ou d'un site officiel.
2. Citations mot pour mot, à la première personne ; jamais de discours indirect ni de reformulation entre guillemets.
3. Neutralité : résumés factuels, aucun adjectif de jugement, même traitement pour tous les candidats.
4. Jamais de sondage (interdiction légale la veille et le jour du vote ; choix éditorial le reste du temps).
5. Photos : uniquement via `scripts/photos.py` (licences libres, crédit affiché).
6. Dans le doute, ne rien publier.

Le détail est dans `MISE_A_JOUR.md`, qui sert aussi de consigne à la mise à jour automatique.

## Mise à jour automatique

Une routine cloud Claude (tous les jours à 7 h, heure de Paris) suit `MISE_A_JOUR.md` : recherche d'actualité, mise à jour de `data.json`, scripts ci-dessus, entrée dans `JOURNAL.md`, push sur `main`.
Avant de modifier les données à la main, faire `git pull` pour récupérer ses derniers changements.

## Crédits Netlify (forfait gratuit : 300 crédits par mois, renouvelés le 25)

Chaque mise en ligne en production (push sur `main` qui modifie le site) coûte 15 crédits ; la bande passante coûte 20 crédits par Go. Crédits épuisés = site coupé jusqu'au mois suivant.
Donc : regrouper les changements en un seul push, ne jamais pousser pour rien. `netlify.toml` annule la mise en ligne quand seuls des fichiers internes changent (journal, consignes, scripts). Les aperçus de branche et de pull request sont gratuits.
Le propriétaire envisagera un forfait payant (Personal, 9 $/mois, 1 000 crédits) à 80 % de consommation.
Relire de temps en temps ses ajouts : erreurs déjà vues = citation au discours indirect, étiquette de parti approximative.

## Référencement et mesure

- Google Search Console validée (propriété domaine). `sitemap.xml` et `robots.txt` à la racine.
- Statistiques : GoatCounter (code `quiditquoi2027`, sans cookies), script présent sur toutes les pages.
- Toute nouvelle page doit reprendre les balises `<head>` d'une page existante (canonical, Open Graph, icônes) et le script GoatCounter, puis être ajoutée à `scripts/generer_sitemap.py`.

## Mentions légales

Éditeur anonyme (LCEN art. 6-III-2), hébergeur Netlify. Page `a-propos.html`.
Avant d'ajouter de la publicité : mettre à jour la politique de confidentialité et prévoir un bandeau de consentement conforme.
