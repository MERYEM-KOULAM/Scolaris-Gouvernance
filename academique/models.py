from django.db import models
from django.conf import settings

class Cycle(models.Model):
    nom = models.CharField(max_length=50) # Ex: Licence, Master
    duree_annees = models.IntegerField(default=3)
    
    def __str__(self):
        return self.nom

class Filiere(models.Model):
    nom = models.CharField(max_length=100) # Ex: Génie Logiciel
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='filieres')
    # On utilise une string 'rh.Departement' pour éviter les erreurs d'import circulaire
    departement = models.ForeignKey('rh.Departement', on_delete=models.CASCADE, related_name='filieres_academiques')
    
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'role': 'PROFESSEUR'}
    )

    def __str__(self):
        return f"{self.nom} ({self.cycle.nom})"

class Cours(models.Model):
    code = models.CharField(max_length=20, unique=True) # Ex: INFO101
    nom = models.CharField(max_length=200)
    volume_horaire = models.IntegerField(help_text="Volume horaire total en heures")
    description = models.TextField(blank=True)
    
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='cours')
    semestre = models.IntegerField(default=1)
    
    professeur_principal = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'role': 'PROFESSEUR'},
        related_name='cours_enseignes'
    )

    def __str__(self):
        return f"{self.code} - {self.nom}"

class SupportCours(models.Model):
    TYPES = (
        ('COURS', 'Cours Magistral'),
        ('TD', 'Travaux Dirigés (TD)'),
        ('TP', 'Travaux Pratiques (TP)'),
    )
    
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='supports')
    titre = models.CharField(max_length=200)
    type_support = models.CharField(max_length=10, choices=TYPES)
    # Les fichiers iront dans le dossier media/supports_cours/
    fichier = models.FileField(upload_to='supports_cours/') 
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} ({self.type_support})"

class Seance(models.Model):
    JOURS = (
        ('LUNDI', 'Lundi'), ('MARDI', 'Mardi'), ('MERCREDI', 'Mercredi'),
        ('JEUDI', 'Jeudi'), ('VENDREDI', 'Vendredi'), ('SAMEDI', 'Samedi')
    )
    
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='seances')
    jour = models.CharField(max_length=10, choices=JOURS)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    salle = models.CharField(max_length=50) 
    
    def __str__(self):
        return f"{self.cours.nom} - {self.get_jour_display()} {self.heure_debut}"

class Devoir(models.Model):
    """Modèle pour gérer les devoirs assignés aux étudiants"""
    STATUTS = (
        ('ACTIF', 'Actif'),
        ('TERMINE', 'Terminé'),
        ('ARCHVE', 'Archivé'),
    )
    
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='devoirs')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_limite = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUTS, default='ACTIF')
    support_cours = models.ForeignKey(
        SupportCours, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='devoirs',
        help_text="Support de cours associé (TD ou TP)"
    )
    
    def __str__(self):
        return f"{self.titre} - {self.cours.code}"

class SoumissionDevoir(models.Model):
    """Modèle pour les soumissions d'étudiants"""
    STATUTS = (
        ('EN_ATTENTE', 'En attente'),
        ('SOUMIS', 'Soumis'),
        ('CORRIGE', 'Corrigé'),
        ('NOTE', 'Noté'),
    )
    
    devoir = models.ForeignKey(Devoir, on_delete=models.CASCADE, related_name='soumissions')
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'ETUDIANT'},
        related_name='soumissions_devoirs'
    )
    fichier = models.FileField(upload_to='soumissions_devoirs/')
    date_soumission = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True)
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    feedback_professeur = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_ATTENTE')
    
    class Meta:
        unique_together = ('devoir', 'etudiant')
    
    def __str__(self):
        return f"{self.etudiant} - {self.devoir.titre}"

class SoumissionTDTP(models.Model):
    """Modèle pour les soumissions de TD et TP"""
    STATUTS = (
        ('EN_ATTENTE', 'En attente'),
        ('SOUMIS', 'Soumis'),
        ('CORRIGE', 'Corrigé'),
        ('NOTE', 'Noté'),
    )
    
    FORMATS_ACCEPTES = (
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel (.xlsx, .xls)'),
        ('WORD', 'Word (.docx, .doc)'),
    )
    
    support_cours = models.ForeignKey(
        SupportCours, 
        on_delete=models.CASCADE, 
        related_name='soumissions_tdtp',
        limit_choices_to={'type_support__in': ['TD', 'TP']}
    )
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'ETUDIANT'},
        related_name='soumissions_tdtp'
    )
    fichier = models.FileField(upload_to='soumissions_tdtp/')
    format_fichier = models.CharField(max_length=20, choices=FORMATS_ACCEPTES, default='PDF')
    date_soumission = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True)
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    feedback_professeur = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_ATTENTE')
    
    class Meta:
        unique_together = ('support_cours', 'etudiant')
    
    def __str__(self):
        return f"{self.etudiant} - {self.support_cours.titre}"

# ... Vos imports existants ...

class Annonce(models.Model):
    CIBLES = (
        ('TOUS', 'Tout le monde'),
        ('ETUDIANTS', 'Étudiants uniquement'),
        ('PROFESSEURS', 'Professeurs uniquement'),
    )
    
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cible = models.CharField(max_length=20, choices=CIBLES, default='TOUS')
    important = models.BooleanField(default=False, help_text="Épingler cette annonce")

    def __str__(self):
        return self.titre