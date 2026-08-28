# Vélo'v Tabareau

**[Voir la démo en ligne →](https://mikescops.github.io/velov-dashboard/)**

Tableau de bord personnel pour suivre en direct la station Vélo'v **TABAREAU** (Lyon, Croix-Rousse) : disponibilité des vélos électriques, places libres pour se garer, stations de secours à proximité, carte interactive et itinéraire vers une destination avec estimation du dénivelé au retour.

Page 100 % statique — un seul fichier `index.html`, sans build, sans backend, sans clé API — qui interroge des APIs publiques en direct depuis le navigateur.

## Fonctionnalités

- **Vélos électriques en priorité** : la métrique mise en avant (couleurs, alertes, meilleure alternative) est le nombre de vélos électriques disponibles, pas le total — les mécaniques sont affichés à part, en secours.
- **Bannière d'état** (OK / à surveiller / critique) résumant en un coup d'œil s'il faut faire attention avant de partir ou de rentrer.
- **Stations de secours à proximité**, choisies volontairement à la même altitude que Tabareau pour ne jamais imposer une côte en plus si tu dois te rabattre sur une autre station.
- **Carte interactive** (Leaflet / OpenStreetMap) avec un marqueur par station, coloré selon son état, et la meilleure alternative mise en évidence.
- **Planificateur de trajet** : tape une destination, l'itinéraire se trace sur la carte avec distance, temps estimé à vélo et dénivelé du retour (utile pour savoir si tu auras besoin d'un vélo électrique en rentrant).
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

## Personnaliser pour une autre station

Tout se configure en haut du `<script>` dans `index.html` :

- `TABAREAU` — la station suivie en priorité (id, nom, coordonnées, capacité).
- `NEARBY` — la liste des stations de secours affichées (id, nom, adresse, coordonnées, capacité, distance).

L'identifiant de station (`station_id`) se trouve dans le flux [`station_information.json`](https://download.data.grandlyon.com/files/rdata/jcd_jcdecaux.jcdvelov/station_information.json) du portail Grand Lyon.

## Licence

[MIT](LICENSE) — le code de ce projet est libre d'utilisation. Les données affichées restent soumises aux licences de leurs fournisseurs respectifs (Métropole de Lyon, OpenStreetMap, Open-Meteo).
