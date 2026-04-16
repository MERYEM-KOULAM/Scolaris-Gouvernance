from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_rh, name='dashboard_rh'),
    path('mon-profil/', views.profil_rh, name='profil_rh'),
    path('employes/', views.liste_employes, name='liste_employes'),
    path('departements/', views.liste_departements, name='liste_departements'),
    path('employes/recruter/', views.recruter_employe, name='recruter_employe'),
    path('contrats/nouveau/', views.nouveau_contrat, name='nouveau_contrat'),
    path('employes/<int:employe_id>/', views.dossier_employe, name='dossier_employe'),
]