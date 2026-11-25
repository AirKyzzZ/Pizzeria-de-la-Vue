# La Pizzeria de la Vue

Une application web moderne de commande de pizzas développée avec Vue 3 et Vite.

## Description

La Pizzeria de la Vue est une application de e-commerce permettant aux utilisateurs de parcourir un catalogue de pizzas, de gérer leur panier et de passer des commandes en ligne.

## Fonctionnalités principales

### Catalogue de pizzas
- 8 pizzas disponibles avec descriptions et prix
- Images et animations interactives au survol
- Ajout/retrait de pizzas au panier directement depuis la page d'accueil

### Gestion du panier
- Visualisation des articles sélectionnés
- Modification des quantités
- Calcul automatique du total
- Suggestions de pizzas non commandées
- Formulaire de paiement

### Système de comptes utilisateurs
- Création de compte avec validation sécurisée du mot de passe
- Connexion/déconnexion
- Stockage persistant des comptes (localStorage)
- Page de profil utilisateur

### Interface utilisateur
- Thème clair/sombre
- Navigation fluide entre les pages
- Bouton de retour en haut de page
- Design responsive

### Pages informatives
- Notre histoire
- Nos valeurs
- Mentions légales
- CGV
- Politique de confidentialité
- Contact et horaires

## Technologies utilisées

- Vue 3 (Composition API)
- Vite
- JavaScript ES6+
- CSS3

## Installation

```sh
npm install
```

## Démarrage

### Mode développement

```sh
npm run dev
```

### Build pour la production

```sh
npm run build
```

## Structure du projet

- `src/Accueil.vue` - Page d'accueil avec le catalogue de pizzas
- `src/Panier.vue` - Gestion du panier et paiement
- `src/Compte.vue` - Création de compte
- `src/Connexion.vue` - Connexion utilisateur
- `src/MonCompte.vue` - Profil utilisateur
- `src/Pizzas.js` - Store des pizzas et gestion du panier
- `src/UserStore.js` - Gestion des comptes utilisateurs
- `src/ThemeStore.js` - Gestion du thème clair/sombre

## Configuration IDE recommandée

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

## Tests de charge (Locust)

Atelier 3 de méthodologie de tests, fait à deux (Maxime Mansiet et Simon Godard) alors que le sujet demande des groupes de 3 ou 4.

### Installation

```sh
cd test/load
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Le `requirements.txt` vient d'un `pip freeze` dans ce venv, toutes les dépendances sont donc figées.

### Lancement

On teste le build de prod servi par `vite preview` sur un port fixe :

```sh
npm run build
npm run preview -- --port 4173 --strictPort
```

Puis dans un autre terminal, depuis la racine du projet. Le run léger :

```sh
test/load/.venv/bin/locust -f test/load/locustfile.py --headless -u 20 -r 5 -t 60s \
  --host http://localhost:4173 --csv test/load/results/leger --html test/load/results/leger.html
```

La montée jusqu'à 800 users. Locust tourne sur 4 processus, sinon il sature son propre CPU vers 450 users et fausse les mesures :

```sh
test/load/.venv/bin/locust -f test/load/locustfile.py --headless --processes 4 -u 800 -r 4 -t 210s \
  --host http://localhost:4173 --csv test/load/results/montee --csv-full-history --html test/load/results/montee.html
```

Sans `--headless`, l'interface web de Locust est sur http://localhost:8089. Les CSV, les rapports HTML et une capture de l'interface sont dans `test/load/results/`.

### Ce qu'on mesure

L'appli n'a ni routeur ni backend. Toutes les pages sont des vues de la même URL `/`, rendues côté client depuis un seul bundle JS, et les données (pizzas, panier, compte) restent en mémoire. Côté serveur, une page c'est donc le shell (`/`, le JS, le CSS, le favicon et le logo, 229 Ko) plus les images affichées par la vue.

Chaque tâche Locust affiche une vue avec un cache vide, comme un premier chargement, puis envoie une ligne `PAGE` avec le temps de chargement complet (requêtes en série) et le poids total. Les lignes `GET` gardent le détail par fichier. Poids des tâches : accueil 10, une des 10 pages sans image au hasard 4, panier 3, commande (accueil puis POST du paiement) 2.

Les formulaires (paiement, création de compte, connexion) ne partent jamais vers un serveur. La tâche commande poste quand même les champs du paiement avec `self.client.post` et vérifie que le serveur statique refuse (404 avec `vite preview`), pour montrer qu'il n'y a rien derrière.

### Résultats

Mesuré sur un MacBook Pro M3 Pro (11 cœurs, 18 Go), avec `vite preview` et Locust sur la même machine, donc sans vrai réseau.

Run léger, 20 users pendant 60 s : 75 requêtes HTTP/s, aucun échec.

| Page | Poids | p50 | p95 |
|---|---|---|---|
| Accueil | 8,6 Mo | 22 ms | 46 ms |
| Panier | 6,5 Mo | 20 ms | 44 ms |
| Les 10 pages sans image | 229 Ko | 7 à 15 ms | 10 à 25 ms |
| POST paiement (404) | | 1 ms | 1 ms |

Montée de 0 à 800 users (+4 par seconde), 339 189 requêtes, aucun échec. Le débit est calculé à partir des lignes `PAGE` et du poids de chaque page.

| Users | Requêtes HTTP/s | Débit servi | Accueil p50 | Accueil p95 |
|---|---|---|---|---|
| 0 à 99 | 115 | 67 Mo/s | 23 ms | 38 ms |
| 100 à 199 | 439 | 252 Mo/s | 20 ms | 56 ms |
| 200 à 299 | 806 | 471 Mo/s | 20 ms | 82 ms |
| 300 à 399 | 1 162 | 676 Mo/s | 25 ms | 138 ms |
| 400 à 499 | 1 510 | 886 Mo/s | 35 ms | 203 ms |
| 500 à 599 | 1 862 | 1 090 Mo/s | 39 ms | 290 ms |
| 600 à 699 | 2 131 | 1 244 Mo/s | 206 ms | 863 ms |
| 700 à 799 | 2 311 | 1 351 Mo/s | 469 ms | 1 368 ms |

Ça décroche vers 600 users : le débit plafonne autour de 2 200 requêtes/s et la médiane de l'accueil passe de 40 à 200 ms, puis le p95 dépasse la seconde après 700 users.

On a aussi comparé avec `python3 -m http.server` sur `dist/`, 300 users pendant 60 s (fichiers `comparaison_*`). Une fois la montée passée il répond plus vite (p95 accueil 33 ms contre 170 ms pour `vite preview`), mais il coupe 4,3 % des connexions pendant la montée à 50 users/s. `vite preview` n'a eu aucun échec, c'est lui qu'on a gardé pour les mesures.

## Known issues

Tout a été mesuré en local. Sur un vrai serveur c'est le réseau qui lâchera en premier : avec ce mélange, chaque user tire environ 1,9 Mo/s, un lien à 1 Gbit/s (125 Mo/s) sature donc vers 65 users (calcul, pas mesuré).

1. **Accueil, 8,6 Mo par visite.** Les 8 photos de pizzas font 8,4 Mo à elles seules, en 1024×1024 alors qu'elles sont affichées en 150×150. C'est la page la plus lourde et la première à ralentir : p95 de 46 ms à 20 users, 290 ms vers 550 users, plus d'une seconde après 700. À corriger : redimensionner en 300×300 (écrans retina) et compresser. Essai avec `sips` en JPEG qualité 75 : les 8 images passent à 290 Ko au total, soit 96 % de moins. On peut ajouter du WebP et `loading="lazy"`.
2. **`vumarine.jpg` et `vupicante.jpg` sont des PNG.** Elles ont l'extension `.jpg` mais ce sont des PNG de 1,97 et 1,88 Mo, servies en `image/jpeg`. Ce sont les deux GET les plus lents de la montée (p95 190 et 170 ms, contre 59 à 110 ms pour les autres photos). À corriger : les convertir en vrai JPEG, 35 et 38 Ko en 300×300.
3. **Panier, 6,5 Mo.** Les suggestions affichent les mêmes photos en pleine taille dans des vignettes de 100×100. p95 de 750 ms sur la montée. À corriger : réutiliser les vignettes de l'accueil.
4. **Pas de compression.** `vite preview` envoie le JS (77,6 Ko) et le CSS (10,4 Ko) sans gzip ni brotli, sur toutes les pages. En gzip ils font 29 Ko et 2 Ko. À corriger : servir `dist/` derrière nginx ou Caddy avec gzip ou brotli, ou précompresser au build.
5. **`Cache-Control: no-cache` partout.** Même `/assets/index-[hash].js`, dont le nom change à chaque build, doit être revalidé. Un visiteur qui revient sur le site refait 13 requêtes (des 304) avant d'afficher l'accueil. À corriger : `max-age=31536000, immutable` sur `/assets`, un `max-age` sur `/images`, et `no-cache` seulement sur `index.html`.
6. **Favicon de 42 Ko sur toutes les pages.** `favicon.png` fait 295×303 pour une icône d'onglet. À corriger : une version en 48 px pèse 3 Ko.
7. **Pas d'URL par page.** Sans routeur, un F5 sur n'importe quelle page ramène à l'accueil et recharge ses 8,6 Mo, et le panier en mémoire est perdu. À corriger : `vue-router` et le panier dans `localStorage`.
