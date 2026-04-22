from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours
from scolarite.models import DossierEtudiant
from evaluation.models import Note


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



# les onctions suivants a deplacer au fichier services/notes_service.py 
def traiter_notes(request, cours, etudiants):
    types_notes = ['CC', 'TP', 'EXAM']

    for etudiant in etudiants:
        for type_eval in types_notes:
            # On construit le nom du champ attendu dans le formulaire
            champ = f"note_{type_eval.lower()}_{etudiant.id}"
            valeur = request.POST.get(champ)
            sauvegarder_note(cours, etudiant, type_eval, valeur, request.user)


def sauvegarder_note(cours, etudiant, type_eval, valeur, user):
    if valeur:
        valeur = valeur.replace(',', '.')
        Note.objects.update_or_create(
            etudiant=etudiant, cours=cours, type_eval=type_eval,
            defaults={'valeur': valeur, 'auteur_saisie': user}
        )
    else:
        # Suppression si champ vide 
        Note.objects.filter(etudiant=etudiant, cours=cours, type_eval=type_eval).delete()

def preparer_affichage_notes(cours, etudiants):
    mapping = {'CC': 'cc', 'TP': 'tp', 'EXAM': 'exam'}
    notes_data = {}

    for n in Note.objects.filter(cours=cours):
        notes_data.setdefault(n.etudiant.id, {'cc': '','tp': '','exam': ''})

        key = mapping.get(n.type_eval)
        if key:
            notes_data[n.etudiant.id][key] = str(n.valeur)

    # transformer en liste pour template
    return [
        (etud, notes_data.get(etud.id, {'cc': '', 'tp': '', 'exam': ''}))
        for etud in etudiants
    ]