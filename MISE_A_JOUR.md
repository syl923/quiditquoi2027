# Consignes de la mise à jour quotidienne

Ce fichier est lu par la tâche automatique qui met à jour le site chaque jour.
Il fait foi : en cas de doute, la règle la plus prudente l'emporte.

## Objectif

Mettre à jour `data/data.json` avec l'actualité des dernières 48 heures sur la présidentielle 2027 :
- nouvelles candidatures, retraits, résultats de primaires, changements de statut ;
- déclarations marquantes des candidats (citations exactes) ;
- nouvelles propositions de programme sur les thèmes du site ;
- dates du calendrier électoral qui se précisent.

## Règles absolues

1. **Aucune information sans source.** Chaque ajout pointe vers un article accessible, publié par un média identifiable (LCP, Public Sénat, Toute l'Europe, RTS, CNews, Wikipédia, sites officiels : vie-publique.fr, conseil-constitutionnel.fr, info.gouv.fr…). Pas de blogs, forums, réseaux sociaux anonymes ni sites agrégateurs inconnus.
2. **Citations mot pour mot.** Le champ `texte` d'une déclaration reprend exactement les mots entre guillemets de la source. Si la citation exacte n'est pas lisible dans la source, ne pas l'ajouter. Pas de discours indirect ni de propos rapportés à la troisième personne (« il était hors de question de se mettre derrière… ») : uniquement des phrases prononcées à la première personne, telles quelles.
3. **Neutralité.** Résumés factuels, sans adjectif de jugement (« choc », « démagogique », « courageux »…). Même traitement pour tous les candidats.
4. **Ne jamais supprimer** une déclaration ou une position existante, sauf si une source fiable prouve qu'elle est fausse. Dans ce cas, la corriger.
5. **Doute = on s'abstient.** Information contradictoire entre sources, rumeur, « selon nos informations » non confirmé : ne pas publier.
6. **Sondages** : ne pas en publier. Interdiction légale de toute publication de sondage la veille et le jour de chaque tour (17-18 avril et 1er-2 mai 2027).

## Format des données (`data/data.json`)

- `sources` : dictionnaire `clé -> { titre, url }`. Créer une clé courte et unique pour chaque nouvel article (ex. `lcpFaurePrimaire`). Le titre commence par le nom du média, et contient la date de l'article si connue.
- `candidats` : `id` (prénom-nom en minuscules sans accents), `nom`, `parti`, `couleur` (#rrggbb), `statut` (`declare` | `primaire` | `pressenti` | `retire`), `dateDeclaration` (facultatif), `bio`, `source`.
- `declarations` : `candidat`, `date` (date où la phrase a été prononcée si connue, sinon date de l'article), `theme`, `texte`, `contexte` (média, émission ou événement), `source`.
- `positions` : `candidat`, `theme`, `resume` (1 à 2 phrases), `source`. Une entrée par source ; plusieurs entrées possibles pour un même candidat et un même thème.
- `themes` : ne pas en créer de nouveaux sans nécessité.
- `syntheses` : texte neutre par grand thème ; à ajuster seulement si le paysage change nettement.
- `data/quiz-partis.json` (quiz « Quel parti vous correspond ? ») : quand une nouvelle position sourcée correspond clairement à une réponse existante, ajouter l'id du candidat dans `candidats` et la clé de source dans `sources` de cette réponse. Ne jamais y ajouter un candidat sans position sourcée ; ne pas modifier les questions.
- `calendrier` : `date`, `titre`, `description`, `confirme`, `source`.
- `majLe` : mettre la date du jour à chaque mise à jour.

Garder le format existant (un objet par ligne) pour des historiques lisibles.

## Déroulé

1. Lire `data/data.json` pour connaître l'état actuel.
2. Rechercher l'actualité récente (recherches web ciblées : « présidentielle 2027 », nom de chaque candidat principal, « primaire », « candidature », « retrait »).
3. Ouvrir chaque article retenu pour vérifier l'information et recopier les citations exactes.
4. Modifier `data/data.json`.
5. Lancer `python scripts/valider.py`. S'il échoue, corriger. S'il échoue encore, annuler les modifications et ne rien publier.
6. Lancer `python scripts/photos.py` : ajoute une photo sous licence libre (Wikimedia Commons, avec crédit) aux nouveaux candidats. Ne jamais ajouter de photo à la main depuis un autre site (droits d'auteur). S'il échoue (réseau), continuer sans photo.
7. Lancer `python scripts/generer_pages.py` (régénère les pages `candidats/<id>/`) puis `python scripts/generer_sitemap.py` pour mettre à jour `sitemap.xml` (nouveaux candidats, date).
8. Ajouter une ligne en tête de `JOURNAL.md` : date et résumé des changements.
9. Faire **un seul commit** regroupant tout (message du type `Mise à jour du JJ/MM/AAAA : +2 déclarations, statut de X`), puis **un seul push** sur la branche principale. Relire avant de pousser : une correction poussée ensuite coûte une mise en ligne de plus.

S'il n'y a rien de nouveau et de fiable : ne rien modifier, **ne rien committer et ne rien pousser** (pas même le journal). Vérifier avec `git status` qu'aucun fichier n'a changé.

Pourquoi : chaque mise en ligne en production coûte 15 crédits Netlify, sur 300 par mois en forfait gratuit ; une fois les crédits épuisés, le site est coupé jusqu'au mois suivant. Le fichier `netlify.toml` annule déjà la mise en ligne quand seuls `JOURNAL.md`, `MISE_A_JOUR.md`, `CLAUDE.md`, `README.md` ou `scripts/` ont changé, mais mieux vaut ne pas pousser du tout.
