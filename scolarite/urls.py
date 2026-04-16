from django.urls import path
from . import views
from scolarite import views as scolarite_views

app_name = 'scolarite'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    # --- AJOUTEZ CES LIGNES ---
    # Page liste des demandes
    path('inscriptions/', views.liste_inscriptions, name='liste_inscriptions'),
    
    # Action invisible pour traiter (accepter/refuser)
    path('inscriptions/<int:id_demande>/<str:decision>/', views.traiter_inscription, name='traiter_inscription'),
    # --- NOUVELLE LIGNE ---
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('etudiants/<int:pk>/', views.voir_dossier, name='voir_dossier'),
    path('etudiants/<int:etudiant_id>/note/ajouter/', views.ajouter_note, name='ajouter_note'),
    path('documents/', views.liste_documents, name='liste_documents'),
    path('documents/<int:id_doc>/traiter/', views.traiter_document, name='traiter_document'),
    path('etudiants/<int:etudiant_id>/document/creer/', views.admin_creer_document, name='admin_creer_document'),
    path('profil/', views.profil_scolarite, name='profil_scolarite'),
    # Dans scolarite/urls.py
    path('notes-profs/', views.liste_notes_profs, name='liste_notes_profs'),
    path('notes-profs/<int:id_fichier>/traiter/', views.traiter_fichier_prof, name='traiter_fichier_prof'),
    path('documents/<int:demande_id>/importer/', views.importer_document, name='importer_document'),
    path('candidature/', scolarite_views.page_candidature, name='candidature'),
    path('candidat/dashboard/', views.dashboard_candidat, name='dashboard_candidat'),
]
