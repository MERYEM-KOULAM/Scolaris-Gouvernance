# Test de l'analyse SonarCloud sur une PR
from django.contrib import admin
from .models import Cycle, Filiere, Cours, Seance, Devoir, SoumissionDevoir, SupportCours, SoumissionTDTP

class CoursAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'filiere', 'professeur_principal']
    list_filter = ['filiere', 'professeur_principal']

class SupportCoursAdmin(admin.ModelAdmin):
    list_display = ['titre', 'cours', 'type_support', 'date_ajout']
    list_filter = ['type_support', 'date_ajout']
    search_fields = ['titre', 'cours__nom']

class DevoirAdmin(admin.ModelAdmin):
    list_display = ['titre', 'cours', 'date_limite', 'statut', 'support_cours']
    list_filter = ['statut', 'date_limite']
    search_fields = ['titre', 'cours__nom']

class SoumissionDevoirAdmin(admin.ModelAdmin):
    list_display = ['devoir', 'etudiant', 'date_soumission', 'statut', 'note']
    list_filter = ['statut', 'date_soumission']
    search_fields = ['etudiant__last_name', 'devoir__titre']

class SoumissionTDTPAdmin(admin.ModelAdmin):
    list_display = ['support_cours', 'etudiant', 'format_fichier', 'date_soumission', 'statut', 'note']
    list_filter = ['statut', 'format_fichier', 'date_soumission']
    search_fields = ['etudiant__last_name', 'support_cours__titre']

admin.site.register(Cycle)
admin.site.register(Filiere)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Seance)
admin.site.register(SupportCours, SupportCoursAdmin)
admin.site.register(Devoir, DevoirAdmin)
admin.site.register(SoumissionDevoir, SoumissionDevoirAdmin)
admin.site.register(SoumissionTDTP, SoumissionTDTPAdmin)