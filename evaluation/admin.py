from django.contrib import admin
from .models import Note, HistoriqueNote, Reclamation

# Cette classe permet d'afficher l'historique DANS la page de la note
class HistoriqueNoteInline(admin.TabularInline):
    model = HistoriqueNote
    extra = 0 # On n'affiche pas de lignes vides
    readonly_fields = ('ancienne_valeur', 'nouvelle_valeur', 'date_modification') # Lecture seule pour l'audit
    can_delete = False # On ne doit pas pouvoir effacer l'historique (Audit)

class NoteAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'cours', 'valeur', 'type_eval', 'date_saisie']
    list_filter = ['cours', 'type_eval']
    search_fields = ['etudiant__last_name', 'etudiant__username', 'cours__nom']
    
    # C'est ici qu'on attache l'historique
    inlines = [HistoriqueNoteInline]

class HistoriqueNoteAdmin(admin.ModelAdmin):
    list_display = ['note_concernee', 'ancienne_valeur', 'nouvelle_valeur', 'date_modification']
    list_filter = ['date_modification']

admin.site.register(Note, NoteAdmin)
admin.site.register(HistoriqueNote, HistoriqueNoteAdmin)
admin.site.register(Reclamation)