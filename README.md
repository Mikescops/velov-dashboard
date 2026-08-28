# Vélo'v Tabareau

**[Voir la démo en ligne →](https://mikescops.github.io/velov-dashboard/)**

Tableau de bord personnel pour suivre en direct la station Vélo'v **TABAREAU** (Lyon, Croix-Rousse) : disponibilité des vélos électriques, places libres pour se garer, stations de secours à proximité, carte interactive, itinéraire vers une destination avec profil de dénivelé, et tendances horaires basées sur l'historique.

Page 100 % statique — un seul fichier `index.html`, sans build, sans backend, sans clé API — qui interroge des APIs publiques en direct depuis le navigateur. Installable comme une app (PWA) et utilisable hors connexion grâce à un cache local des dernières données connues.

## Fonctionnalités

- **Vélos électriques en priorité** : la métrique mise en avant (couleurs, alertes, meilleure alternative) est le nombre de vélos électriques disponibles, pas le total — les mécaniques sont affichés à part, en secours.
- **Bannière d'état** (OK / à surveiller / critique), toujours visible quel que soit l'onglet, pour savoir en un coup d'œil s'il faut faire attention avant de partir ou de rentrer.
- **Quatre vues dédiées** plutôt qu'une longue page unique :
  - **Accueil** — disponibilité de Tabareau et des stations de secours à proximité.
  - **Carte** — carte interactive (Leaflet / OpenStreetMap), un marqueur par station coloré selon son état.
  - **Itinéraire** — planificateur de trajet avec destinations récentes/favorites.
  - **Tendances** — disponibilité moyenne par heure, calculée sur l'historique collecté automatiquement.
- **Stations de secours à proximité**, choisies volontairement à la même altitude que Tabareau pour ne jamais imposer une côte en plus si tu dois te rabattre sur une autre station.
- **Planificateur de trajet** avec profil de dénivelé complet (plusieurs points échantillonnés le long du tracé, pas juste départ/arrivée) et une petite courbe d'altitude, pour savoir si le retour grimpe.
- **Destinations récentes** : les lieux recherchés sont mémorisés (localStorage) et réapparaissent en un clic ; possibilité d'épingler tes trajets fréquents pour les garder en haut de la liste.
- **Tendances horaires** : un historique (collecté automatiquement toutes les 15 minutes par une GitHub Action, voir plus bas) permet d'afficher la disponibilité moyenne par heure et de repérer les créneaux à éviter.
- **Résilience hors ligne** : les dernières données reçues sont gardées en cache local ; si le réseau ou l'API est indisponible, le tableau de bord reste utilisable et indique l'ancienneté des données affichées.
- **Installable (PWA)** : "Ajouter à l'écran d'accueil" sur iOS/Android/desktop pour l'ouvrir en plein écran comme une vraie app.
- **Météo locale** : température et alerte pluie sur les prochaines heures.
- Rafraîchissement automatique toutes les 60 secondes.

## Sources de données

Aucune n'exige de clé API ; toutes sont interrogées directement depuis le navigateur du visiteur.

| Donnée | Source |
|---|---|
| Disponibilité temps réel des stations (GBFS) | [Métropole de Lyon — data.grandlyon.com](https://data.grandlyon.com/portail/fr/jeux-de-donnees/stations-velo-v-metropole-lyon-disponibilites-temps-reel/api) |
| Géocodage des adresses | [Base Adresse Nationale](https://adresse.data.gouv.fr/api-doc/adresse) |
| Calcul d'itinéraire | [OSRM](http://project-osrm.org/) (instance publique de démonstration) |
| Météo et altitude | [Open-Meteo](https://open-meteo.com/) |
| Fond de carte | [OpenStreetMap](https://www.openstreetmap.org/copyright) via [Leaflet](https://leafletjs.com/) |

> Le service d'itinéraire public (OSRM) ne propose pas de profil vélo dédié : le tracé suit le réseau routier général, pas forcément les pistes cyclables. Le dénivelé est une estimation basée sur un modèle numérique de terrain (résolution ~90 m).

## Historique et tendances

Le fichier [`data/history.jsonl`](data/history.jsonl) contient un relevé de la station Tabareau par ligne (`{"t":epoch,"elec":n,"meca":n,"docks":n}`). Il est alimenté automatiquement par [`.github/workflows/collect-data.yml`](.github/workflows/collect-data.yml), qui tourne toutes les 15 minutes, appelle [`scripts/collect.py`](scripts/collect.py) et committe le résultat. L'historique de plus de 120 jours est purgé automatiquement pour que le fichier reste léger.

Pour que la collecte fonctionne sur ton dépôt : **Settings → Actions → General → Workflow permissions**, choisir *Read and write permissions* (nécessaire pour que le workflow puisse committer). Le premier relevé n'apparaît qu'après le premier déclenchement du workflow ; l'onglet Tendances affiche un message d'attente tant qu'il n'y a pas assez de données (au moins 50 relevés, soit un peu plus de 12h).

## Installer l'app (PWA)

Depuis un navigateur mobile (Safari sur iOS, Chrome sur Android) : menu de partage → *Ajouter à l'écran d'accueil*. Sur desktop (Chrome/Edge) : icône d'installation dans la barre d'adresse. L'app s'ouvre alors en plein écran, avec sa propre icône, et reste consultable brièvement hors connexion (coquille mise en cache par [`sw.js`](sw.js) ; les données en direct, elles, dépendent toujours du réseau — sinon les dernières données connues sont affichées).

## Personnaliser pour une autre station

Tout se configure en haut du `<script>` dans `index.html` :

- `TABAREAU` — la station suivie en priorité (id, nom, coordonnées, capacité).
- `NEARBY` — la liste des stations de secours affichées (id, nom, adresse, coordonnées, capacité, distance).

L'identifiant de station (`station_id`) se trouve dans le flux [`station_information.json`](https://download.data.grandlyon.com/files/rdata/jcd_jcdecaux.jcdvelov/station_information.json) du portail Grand Lyon. Pour suivre une autre station dans `scripts/collect.py`, changer la constante `STATION_ID`.

## Licence

[MIT](LICENSE) — le code de ce projet est libre d'utilisation. Les données affichées restent soumises aux licences de leurs fournisseurs respectifs (Métropole de Lyon, OpenStreetMap, Open-Meteo).
