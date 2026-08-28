# Vélo'v Tabareau

Tableau de bord personnel pour suivre en direct la station Vélo'v **TABAREAU** (Lyon, Croix-Rousse) : disponibilité des vélos électriques, places libres pour se garer, stations de secours à proximité, carte et itinéraire vers une destination avec estimation du dénivelé au retour.

Page 100% statique (HTML/CSS/JS, aucun backend, aucune clé API) qui interroge en direct, depuis le navigateur :

- [GBFS Vélo'v — Métropole de Lyon](https://data.grandlyon.com/portail/fr/jeux-de-donnees/stations-velo-v-metropole-lyon-disponibilites-temps-reel/api) — disponibilité temps réel des stations
- [Base Adresse Nationale](https://adresse.data.gouv.fr/api-doc/adresse) — géocodage des adresses
- [OSRM](http://project-osrm.org/) — calcul d'itinéraire
- [Open-Meteo](https://open-meteo.com/) — météo et altitude
- [OpenStreetMap](https://www.openstreetmap.org/copyright) / [Leaflet](https://leafletjs.com/) — fond de carte

## Publier le site

Le fichier `index.html` est autonome : il suffit de l'héberger tel quel sur n'importe quel hébergeur statique.

### Option 1 — GitHub Pages (recommandé, gratuit)

```bash
git remote add origin https://github.com/<ton-compte>/velov-tabareau.git
git branch -M main
git push -u origin main
```

Puis dans les réglages du repo GitHub : **Settings → Pages → Source: Deploy from a branch → Branch: main / (root)**.
Le site sera disponible à `https://<ton-compte>.github.io/velov-tabareau/` en quelques minutes.

### Option 2 — Netlify Drop (le plus rapide, sans compte)

Glisser le fichier `index.html` sur [app.netlify.com/drop](https://app.netlify.com/drop) → URL générée instantanément.

### Option 3 — Cloudflare Pages

Même principe que GitHub Pages : connecter le repo GitHub depuis le tableau de bord Cloudflare Pages, dossier de build = racine, pas de commande de build.

## Personnaliser

Toutes les stations suivies (Tabareau + stations de secours) sont définies en haut du `<script>` dans `index.html` (`TABAREAU` et `NEARBY`), avec leurs coordonnées, capacité et distance. Pour suivre une autre station, il suffit de changer ces valeurs — l'identifiant (`station_id`) se trouve dans le flux `station_information.json` du portail Grand Lyon.
