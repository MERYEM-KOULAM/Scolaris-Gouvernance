from django.db import models
from django.conf import settings # Pour faire référence à votre User personnalisé

class Departement(models.Model):
    nom = models.CharField(max_length=100, unique=True) # Ex: Mathématiques, Informatique
    description = models.TextField(blank=True)
    
    # Le chef est un Professeur (User)
    chef = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'PROFESSEUR'}, # Sécurité : seul un prof peut être chef
        related_name='departement_dirige'
    )

    def __str__(self):
        return self.nom

class Contrat(models.Model):
    TYPE_CONTRAT = (('CDI', 'Contrat à Durée Indéterminée'), ('CDD', 'Contrat à Durée Déterminée'), ('VACATAIRE', 'Vacataire'))
    
    professeur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'PROFESSEUR'},
        related_name='contrats'
    )
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, related_name='professeurs')
    
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    salaire_mensuel = models.DecimalField(max_digits=10, decimal_places=2)
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT)
    fichier_contrat = models.FileField(upload_to='contrats_rh/', blank=True, null=True) # PDF du contrat signé

    def __str__(self):
        return f"Contrat de {self.professeur} ({self.type_contrat})"