from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Cycle, Filiere, Cours, Devoir
from django.utils import timezone

User = get_user_model()

class ModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="prof", role="PROFESSEUR")
        self.cycle = Cycle.objects.create(nom="Licence")
        
        # ⚠️ adapte si Departement obligatoire chez toi
        from rh.models import Departement
        self.dept = Departement.objects.create(nom="Informatique", chef=self.user)

        self.filiere = Filiere.objects.create(
            nom="GL",
            cycle=self.cycle,
            departement=self.dept,
            responsable=self.user
        )

    def test_create_cours(self):
        cours = Cours.objects.create(
            code="INFO101",
            nom="Algo",
            volume_horaire=30,
            filiere=self.filiere,
            professeur_principal=self.user
        )

        self.assertEqual(cours.nom, "Algo")

class ProfViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="prof", password="1234", role="PROFESSEUR")

    def test_dashboard_prof_access(self):
        self.client.login(username="prof", password="1234")
        
        response = self.client.get(reverse('dashboard_prof'))

        self.assertEqual(response.status_code, 200)

    def test_dashboard_refuse_non_prof(self):
        user2 = User.objects.create_user(username="etud", password="1234", role="ETUDIANT")
        self.client.login(username="etud", password="1234")

        response = self.client.get(reverse('dashboard_prof'))

        self.assertContains(response, "acces_interdit")

    def test_ajout_support(self):
        from .models import Cycle, Filiere, Cours
        from rh.models import Departement

        cycle = Cycle.objects.create(nom="Licence")
        dept = Departement.objects.create(nom="Info", chef=self.user)

        filiere = Filiere.objects.create(
            nom="GL",
            cycle=cycle,
            departement=dept,
            responsable=self.user
        )

        cours = Cours.objects.create(
            code="INFO101",
            nom="Algo",
            volume_horaire=30,
            filiere=filiere,
            professeur_principal=self.user
        )

        self.client.login(username="prof", password="1234")

        response = self.client.post(
            reverse('gerer_supports', args=[cours.id]),
            {
                'titre': 'Chapitre 1',
                'type_support': 'COURS',
            }
        )

        self.assertEqual(response.status_code, 302)  # redirect