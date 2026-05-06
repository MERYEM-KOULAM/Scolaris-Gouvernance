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
    
    if request.method == 'POST':
        for etudiant in etudiants:
            # Fonction locale pour gérer CC, TP, EXAM
            def traiter_note(type_eval, nom_champ):
                valeur_input = request.POST.get(nom_champ)
                
                # Astuce : On remplace la virgule par un point si le prof s'est trompé en tapant
                if valeur_input:
                    valeur_input = valeur_input.replace(',', '.')

                if valeur_input: 
                    # Création ou Mise à jour
                    Note.objects.update_or_create(
                        etudiant=etudiant, cours=cours, type_eval=type_eval,
                        defaults={'valeur': valeur_input, 'auteur_saisie': request.user}
                    )
                else:
                    # Suppression si champ vide 
                    Note.objects.filter(etudiant=etudiant, cours=cours, type_eval=type_eval).delete()

            traiter_note('CC', f'note_cc_{etudiant.id}')
            traiter_note('TP', f'note_tp_{etudiant.id}')
            traiter_note('EXAM', f'note_exam_{etudiant.id}')

        messages.success(request, "Les notes ont été mises à jour.")
        return redirect('saisie_notes', cours_id=cours.id)

    # Préparation des données pour l'affichage
    notes_data = {}
    toutes_notes = Note.objects.filter(cours=cours)
    
    for n in toutes_notes:
        if n.etudiant.id not in notes_data:
            notes_data[n.etudiant.id] = {'cc': '', 'tp': '', 'exam': ''}
        
        # On force la conversion en chaîne de caractères (str)
        # Cela empêche Django de transformer 15.5 en 15,5 (ce qui casse l'affichage)
        valeur_str = str(n.valeur)
        
        if n.type_eval == 'CC': notes_data[n.etudiant.id]['cc'] = valeur_str
        elif n.type_eval == 'TP': notes_data[n.etudiant.id]['tp'] = valeur_str
        elif n.type_eval == 'EXAM': notes_data[n.etudiant.id]['exam'] = valeur_str

    liste_etudiants_notes = []
    for etud in etudiants:
        notes = notes_data.get(etud.id, {'cc': '', 'tp': '', 'exam': ''})
        liste_etudiants_notes.append((etud, notes))
    
    context = { 'cours': cours, 'liste_donnees': liste_etudiants_notes }
    return render(request, 'academique/saisie_notes.html', context)

