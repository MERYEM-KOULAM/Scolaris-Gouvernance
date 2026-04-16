from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Note(models.Model):
    etudiant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'ETUDIANT'})
    cours = models.ForeignKey('academique.Cours', on_delete=models.CASCADE)
    
    TYPE_EVAL = (
        ('CC', 'Contrôle Continu'),
        ('TP', 'Travaux Pratiques'),
        ('EXAM', 'Examen Final')
    )
    
    type_eval = models.CharField(max_length=20, choices=TYPE_EVAL)
    valeur = models.DecimalField(max_digits=4, decimal_places=2) # Note sur 20.00
    coefficient = models.IntegerField(default=1)
    
    date_saisie = models.DateTimeField(auto_now_add=True)
    auteur_saisie = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='notes_saisies')

    def __str__(self):
        return f"{self.valeur}/20 - {self.cours.code} ({self.etudiant})"

class HistoriqueNote(models.Model):
    """ Ce modèle est votre Tableau d'Évolution pour l'Audit """
    note_concernee = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='historique')
    ancienne_valeur = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nouvelle_valeur = models.DecimalField(max_digits=4, decimal_places=2)
    
    date_modification = models.DateTimeField(auto_now_add=True)
    # Pour simplifier, on stocke juste le texte de qui a fait l'action si besoin, 
    # ou on peut lier à un User si on passe l'info via les Vues.
    
    def __str__(self):
        return f"Modif le {self.date_modification} : {self.ancienne_valeur} -> {self.nouvelle_valeur}"

# --- SIGNAL AUTOMATIQUE ---
@receiver(pre_save, sender=Note)
def tracer_changement_note(sender, instance, **kwargs):
    """ 
    Avant de sauvegarder une note, on vérifie si elle existait déjà.
    Si elle change, on crée une ligne dans l'historique.
    """
    if instance.id: # C'est une modification, pas une création
        try:
            ancienne_note = Note.objects.get(id=instance.id)
            if ancienne_note.valeur != instance.valeur:
                HistoriqueNote.objects.create(
                    note_concernee=instance,
                    ancienne_valeur=ancienne_note.valeur,
                    nouvelle_valeur=instance.valeur
                )
        except Note.DoesNotExist:
            pass
class Reclamation(models.Model):
    STATUTS = (('EN_ATTENTE', 'En Attente'), ('TRAITEE', 'Traitée'), ('REJETEE', 'Rejetée'))
    
    etudiant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cours = models.ForeignKey('academique.Cours', on_delete=models.CASCADE)
    message = models.TextField()
    reponse_prof = models.TextField(blank=True, verbose_name="Réponse du professeur")
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_ATTENTE')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Réclamation de {self.etudiant} - {self.cours.nom}"