from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours
from scolarite.models import DossierEtudiant
from .services import traiter_notes, preparer_affichage_notes

@login_required
def saisir_notes(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id, professeur_principal=request.user)
    dossiers = DossierEtudiant.objects.filter(filiere=cours.filiere)
    etudiants = [d.etudiant for d in dossiers]
    
    #traitement des donnees
    if request.method == 'POST':
        traiter_notes(request, cours, etudiants)

        messages.success(request, "Les notes ont été mises à jour.")
        return redirect('saisie_notes', cours_id=cours.id)

    # Préparation des données pour l'affichage
    notes_data = preparer_affichage_notes(cours, etudiants)
    
    context = { 'cours': cours, 'liste_donnees': notes_data }
    return render(request, 'academique/saisie_notes.html', context)
