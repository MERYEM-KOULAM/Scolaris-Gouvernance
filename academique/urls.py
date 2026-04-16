from django.urls import path
from . import views

urlpatterns = [
    # Professeur
    path('tableau-de-bord/', views.tableau_bord_professeur, name='dashboard_prof'),
    path('cours/<int:cours_id>/notes/', views.saisir_notes, name='saisie_notes'),
    path('cours/<int:cours_id>/upload/', views.upload_notes_cours, name='upload_notes_cours'),
    path('cours/<int:cours_id>/supports/', views.gerer_supports, name='gerer_supports'),
    path('emploi-du-temps/', views.mon_emploi_du_temps, name='emploi_du_temps'),
    path('reclamations/', views.liste_reclamations, name='liste_reclamations'),
    path('mon-profil/', views.profil_prof, name='profil_prof'),
    path('devoirs-soumis/', views.voir_devoirs_soumis, name='voir_devoirs_soumis'),
    path('soumission/<int:soumission_id>/evaluer/', views.evaluer_soumission, name='evaluer_soumission'),
    
    # Chef Département
    path('chef-departement/', views.dashboard_chef, name='dashboard_chef'),
    path('chef-departement/cours/', views.gerer_cours_departement, name='gerer_cours_chef'),
    path('chef-departement/planning/', views.planifier_seances_chef, name='planifier_seances_chef'),

    # ETUDIANT
    path('etudiant/tableau-de-bord/', views.dashboard_etudiant, name='dashboard_etudiant'),
    path('etudiant/demander-document/', views.demander_document, name='demander_document'),
    path('etudiant/mes-notes/', views.mes_notes, name='mes_notes'),
    path('etudiant/emploi-du-temps/', views.mon_emploi_temps_etudiant, name='emploi_temps_etudiant'),
    path('etudiant/mes-reclamations/', views.mes_reclamations, name='mes_reclamations'),
    path('etudiant/note/<int:note_id>/reclamation/', views.reclamation_note, name='reclamation_note'),
    path('etudiant/mes-devoirs/', views.mes_devoirs, name='mes_devoirs'),
    path('etudiant/devoir/<int:devoir_id>/soumettre/', views.soumettre_devoir, name='soumettre_devoir'),
    path('etudiant/tdtp/<int:support_id>/soumettre/', views.soumettre_tdtp, name='soumettre_tdtp'),
    path('etudiant/profil/', views.profil_etudiant, name='profil_etudiant'),
    path('etudiant/supports-cours/', views.supports_cours_etudiant, name='supports_cours_etudiant'),

    # ADMINISTRATION (Direction Générale)
    path('direction/dashboard/', views.dashboard_direction, name='dashboard_direction'),
    path('direction/filieres/', views.gerer_filieres_direction, name='gerer_filieres_direction'),
    path('direction/annonces/', views.gerer_annonces_direction, name='gerer_annonces_direction'),
    path('direction/profil/', views.profil_direction, name='profil_direction'),
]