from django.db import models
from django.conf import settings

from core.models import User

class DossierEtudiant(models.Model):
    """ Le profil scolaire de l'étudiant une fois inscrit """
    etudiant = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ETUDIANT'},
        related_name='dossier_scolaire'
    )
    filiere = models.ForeignKey('academique.Filiere', on_delete=models.SET_NULL, null=True)
    date_entree = models.DateField()
    annee_actuelle = models.CharField(max_length=9, default="2025-2026") # Ex: 1ère année
    
    def __str__(self):
        return f"Dossier de {self.etudiant}"

class DemandeInscription(models.Model):
    """ Pour les candidats externes ou étudiants changeant de cycle """
    STATUTS = (('EN_ATTENTE', 'En Attente'), ('ACCEPTEE', 'Acceptée'), ('REFUSEE', 'Refusée'))
    
    candidat = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='demandes_inscription')
    filiere_souhaitee = models.ForeignKey('academique.Filiere', on_delete=models.CASCADE)
    notes_precedentes = models.FileField(upload_to='justificatifs_notes/') # Relevés de notes PDF
    message = models.TextField(blank=True)
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_ATTENTE')
    date_demande = models.DateTimeField(auto_now_add=True)

class DemandeDocument(models.Model):
    TYPE_CHOICES = [
        ('ATTESTATION', 'Attestation de Scolarité'),
        ('RELEVE', 'Relevé de Notes'),
    ]
    STATUT_CHOICES = [
        ('DEMANDE', 'Demandé'),
        ('PRET', 'Prêt / Disponible'), # <--- Quand le fichier est là
        ('REJETE', 'Rejeté'),
    ]

    etudiant = models.ForeignKey(User, on_delete=models.CASCADE)
    type_document = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='DEMANDE')
    
    # AJOUTEZ CETTE LIGNE 👇
    fichier = models.FileField(upload_to='documents_etudiants/', null=True, blank=True)

    def __str__(self):
        return f"{self.etudiant} - {self.type_document}"

# Dans scolarite/models.py

class Note(models.Model):
    SEMESTRES = [
        ('S1', 'Semestre 1'),
        ('S2', 'Semestre 2'),
    ]
    
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    matiere = models.CharField(max_length=100)  # Ex: "Mathématiques", "Java", etc.
    valeur = models.FloatField()  # Ex: 14.5
    semestre = models.CharField(max_length=2, choices=SEMESTRES, default='S1')
    date_saisie = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.matiere} : {self.valeur}/20 ({self.etudiant})"
# Dans scolarite/models.py

class FichierNotes(models.Model):
    ETATS = [
        ('EN_ATTENTE', 'En attente de traitement'),
        ('TRAITE', 'Traité / Saisi'),
    ]

    professeur = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PROFESSEUR'})
    matiere = models.CharField(max_length=100)
    fichier = models.FileField(upload_to='notes_profs_uploads/') # Le fichier Excel/PDF
    date_envoi = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=20, choices=ETATS, default='EN_ATTENTE')

    def __str__(self):
        return f"Notes de {self.matiere} par {self.professeur} ({self.date_envoi.date()})"
