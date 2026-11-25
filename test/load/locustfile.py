import random
import re
import time

from locust import HttpUser, between, task

PIZZA_IMAGES = [
    "/images/vugherita.jpg",
    "/images/4-vues.jpg",
    "/images/vuronni.jpg",
    "/images/vugetarienne.jpg",
    "/images/vueen.jpg",
    "/images/vuzone.jpg",
    "/images/vupicante.jpg",
    "/images/vumarine.jpg",
]
PAGES_SANS_IMAGE = [
    "Créer un compte",
    "Se connecter",
    "Mon compte",
    "Notre histoire",
    "Nos valeurs",
    "Mentions légales",
    "CGV",
    "Politique de confidentialité",
    "Nous contacter",
    "Horaires",
]
COMMANDE = {
    "name": "Jean Test",
    "address": "1 rue de la Pizza, 33000 Bordeaux",
    "card": "4111-1111-1111-1111",
}
REFUS_SANS_BACKEND = {404, 405, 501}


class Visiteur(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        html = self.client.get("/").text
        self.shell = ["/", *re.findall(r'(?:src|href)="(/[^"]+)"', html), "/images/logo.png"]

    def afficher(self, page, images=()):
        debut = time.perf_counter()
        poids = 0
        echecs = []
        for url in [*self.shell, *images]:
            reponse = self.client.get(url)
            poids += len(reponse.content or b"")
            if reponse.status_code != 200:
                echecs.append(url)
        self.environment.events.request.fire(
            request_type="PAGE",
            name=page,
            response_time=(time.perf_counter() - debut) * 1000,
            response_length=poids,
            exception=Exception(f"échec sur {echecs}") if echecs else None,
            context={},
        )

    @task(4)
    def page_sans_image(self):
        self.afficher(random.choice(PAGES_SANS_IMAGE))

    @task(10)
    def accueil(self):
        self.afficher("Accueil", PIZZA_IMAGES)

    @task(3)
    def panier(self):
        dans_le_panier = random.sample(PIZZA_IMAGES, random.randint(1, 3))
        self.afficher("Panier", [image for image in PIZZA_IMAGES if image not in dans_le_panier])

    @task(2)
    def commande(self):
        self.afficher("Accueil", PIZZA_IMAGES)
        with self.client.post(
            "/", data=COMMANDE, name="POST paiement sans backend (refus attendu)", catch_response=True
        ) as reponse:
            if reponse.status_code in REFUS_SANS_BACKEND:
                reponse.success()
            else:
                reponse.failure(f"aucun backend, refus attendu mais reçu {reponse.status_code}")
