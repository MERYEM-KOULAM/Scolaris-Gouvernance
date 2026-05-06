from evaluation.models import Note

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


