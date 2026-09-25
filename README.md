# Qui dit quoi 2027

Site statique (HTML/CSS/JS, sans installation) qui suit la présidentielle 2027 : candidats, déclarations sourcées, tableau des programmes, comparateur par thème, calendrier.

## Voir le site en local

```
py -m http.server 8027
```
puis ouvrir http://localhost:8027 (le site doit être servi par un serveur : ouvrir `index.html` directement ne charge pas les données).

## Mettre à jour le contenu

Tout le contenu est dans `data/data.json`. Les règles (sources obligatoires, citations exactes, neutralité) et le format sont décrits dans [MISE_A_JOUR.md](MISE_A_JOUR.md).

Avant de publier, toujours vérifier :
```
py scripts/valider.py
```

L'historique des mises à jour est tenu dans [JOURNAL.md](JOURNAL.md).

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | Accueil : compte à rebours, dernières déclarations, candidats déclarés |
| `candidats.html` / `candidat.html?id=…` | Liste et fiche candidat |
| `declarations.html` | Toutes les déclarations, filtrables |
| `programmes.html` | Synthèse et tableau des programmes par grand thème |
| `comparateur.html` | Positions côte à côte, thème par thème |
| `calendrier.html` | Dates clés |
| `a-propos.html` | Méthodologie, mentions légales (à compléter) |
| `assets/app.js`, `assets/style.css` | Code et style partagés |
| `scripts/valider.py` | Contrôle de cohérence des données |
