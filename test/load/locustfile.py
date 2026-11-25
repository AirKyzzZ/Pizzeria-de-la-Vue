from locust import HttpUser, between, task


class Visiteur(HttpUser):
    wait_time = between(1, 5)

    @task
    def accueil(self):
        self.client.get("/")
