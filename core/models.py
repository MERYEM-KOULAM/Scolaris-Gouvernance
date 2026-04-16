from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Cette classe représente 'L'Entité Personne'.
    Elle généralise tout le monde : Étudiant, Professeur, Agent RH, Admin.
    """
    
    # Définition stricte des Rôles
    # L'Agent RH et le Professeur sont deux entités totalement différentes.
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur (Direction Générale)'),
        ('RH', 'Responsable RH'),
        ('SCOLARITE', 'Agent de Scolarité'),
        ('PROFESSEUR', 'Professeur'),
        ('ETUDIANT', 'Étudiant'),
        ('CANDIDAT', 'Candidat (Externe)'),
        ('DIRECTEUR', 'Administrateur (Direction Générale)'),
    )
    
    # Champ pour distinguer le rôle de la personne
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Rôle")
    
    # Infos personnelles communes à tous (hérite déjà de nom, prénom, email via AbstractUser)
    civilite = models.CharField(max_length=10, choices=[('M', 'Monsieur'), ('Mme', 'Madame')], blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    photo_profil = models.ImageField(upload_to='profils/', blank=True, null=True)    
    adresse = models.TextField(blank=True)

    # Pour identifier facilement les chefs de département (qui sont des professeurs avec un privilège en plus)
    is_chef_departement = models.BooleanField(default=False, verbose_name="Est Chef de Département")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

    # Petites méthodes utilitaires pour vérifier le rôle dans le code (plus propre)
    @property
    def is_professeur(self):
        return self.role == 'PROFESSEUR'

    @property
    def is_rh(self):
        return self.role == 'RH'
    
    @property
    def is_etudiant(self):
        return self.role == 'ETUDIANT'



class Annonce(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)
    est_urgent = models.BooleanField(default=False)

    def __str__(self):
        return self.titre