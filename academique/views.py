from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import StudentProfileForm
from core.models import User
from .models import Cours, SupportCours, Seance, Devoir, SoumissionDevoir, SoumissionTDTP
from .forms import SupportCoursForm, SoumissionDevoirForm
from scolarite.models import DossierEtudiant, FichierNotes
from evaluation.models import Note, Reclamation
from rh.models import Departement
from .forms import CoursForm
from .forms import SeanceForm
from scolarite.models import DemandeDocument
from .models import Annonce, Filiere
from .forms import AnnonceForm, FiliereForm
from .models import Annonce, Filiere
from .forms import AnnonceForm, FiliereForm
from .forms import StudentProfileForm
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def tableau_bord_professeur(request):
    if request.user.role != 'PROFESSEUR':
        return render(request, 'core/acces_interdit.html')
        
    mes_cours = Cours.objects.filter(professeur_principal=request.user)
    annonces = Annonce.objects.filter(
        cible__in=['TOUS', 'PROFESSEURS']
    ).order_by('-important', '-date_publication')[:3]
    # --- VERIFICATION CHEF ---
    # On regarde si ce prof est chef d'un département
    est_chef = Departement.objects.filter(chef=request.user).exists()
    
    context = {
        'cours': mes_cours,
        'user': request.user,
        'est_chef': est_chef , # <--- On envoie l'info au HTML
        'annonces': annonces
    }
    return render(request, 'academique/dashboard_prof.html', context)

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
                    # Suppression si champ vide (C'est ici que votre suppression fonctionne)
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
        
        # --- CORRECTION ICI ---
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

@login_required
def gerer_supports(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id, professeur_principal=request.user)
    
    if request.method == 'POST':
        form = SupportCoursForm(request.POST, request.FILES)
        if form.is_valid():
            support = form.save(commit=False)
            support.cours = cours
            support.save()
            messages.success(request, "Le support a été ajouté avec succès !")
            return redirect('gerer_supports', cours_id=cours.id)
    else:
        form = SupportCoursForm()

    supports = SupportCours.objects.filter(cours=cours).order_by('-date_ajout')
    context = {'cours': cours, 'form': form, 'supports': supports}
    return render(request, 'academique/gerer_supports.html', context)

@login_required
def mon_emploi_du_temps(request):
    mes_cours = Cours.objects.filter(professeur_principal=request.user)
    seances = Seance.objects.filter(cours__in=mes_cours).order_by('jour', 'heure_debut')
    
    ordre_jours = {'LUNDI': 1, 'MARDI': 2, 'MERCREDI': 3, 'JEUDI': 4, 'VENDREDI': 5, 'SAMEDI': 6}
    seances = sorted(seances, key=lambda x: ordre_jours.get(x.jour, 7))

    return render(request, 'academique/emploi_du_temps.html', {'seances': seances})

@login_required
def liste_reclamations(request):
    mes_cours = Cours.objects.filter(professeur_principal=request.user)
    reclamations = Reclamation.objects.filter(cours__in=mes_cours).order_by('-date_creation')
    
    if request.method == 'POST':
        rec_id = request.POST.get('reclamation_id')
        reponse = request.POST.get('reponse')
        action = request.POST.get('action') 
        
        rec = get_object_or_404(Reclamation, id=rec_id)
        if rec.cours.professeur_principal == request.user:
            rec.reponse_prof = reponse
            rec.statut = action
            rec.date_traitement = timezone.now()
            rec.save()
            messages.success(request, "Réclamation traitée.")
            return redirect('liste_reclamations')

    return render(request, 'academique/reclamations.html', {'reclamations': reclamations})
@login_required
def profil_prof(request):
    # Cette vue fonctionne pour les PROFESSEURS et les CHEFS DE DÉPARTEMENT
    if request.user.role != 'PROFESSEUR': # Un chef est aussi un prof techniquement
         return render(request, 'core/acces_interdit.html')

    user = request.user
    
    # On réutilise le formulaire existant (c'est le même modèle User)
    # Assurez-vous d'avoir importé StudentProfileForm et PasswordChangeForm en haut
    user_form = StudentProfileForm(instance=user)
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        # CAS 1 : Mise à jour des infos (Photo, Nom...)
        if 'update_profile' in request.POST:
            user_form = StudentProfileForm(request.POST, request.FILES, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Vos informations ont été mises à jour.")
                return redirect('profil_prof')
        
        # CAS 2 : Changement de mot de passe
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # Garde la session active
                messages.success(request, "Votre mot de passe a été modifié avec succès.")
                return redirect('profil_prof')
            else:
                messages.error(request, "Erreur dans le changement de mot de passe.")

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'academique/profil.html', context)

@login_required
def voir_devoirs_soumis(request):
    """Voir tous les devoirs soumis par les étudiants pour les cours du professeur"""
    if request.user.role != 'PROFESSEUR':
        return render(request, 'core/acces_interdit.html')
    
    # Récupérer tous les cours du professeur
    mes_cours = Cours.objects.filter(professeur_principal=request.user)
    
    # Récupérer toutes les soumissions de devoirs pour ces cours
    soumissions = SoumissionDevoir.objects.filter(
        devoir__cours__in=mes_cours
    ).select_related('devoir', 'etudiant').order_by('-date_soumission')
    
    # Récupérer toutes les soumissions de TD/TP pour ces cours
    soumissions_tdtp = SoumissionTDTP.objects.filter(
        support_cours__cours__in=mes_cours
    ).select_related('support_cours', 'etudiant').order_by('-date_soumission')
    
    # Filtrage optionnel
    filtre_cours = request.GET.get('cours')
    filtre_statut = request.GET.get('statut')
    filtre_type = request.GET.get('type', 'tous')  # 'tous', 'devoirs', 'tdtp'
    
    if filtre_cours:
        soumissions = soumissions.filter(devoir__cours_id=filtre_cours)
        soumissions_tdtp = soumissions_tdtp.filter(support_cours__cours_id=filtre_cours)
    
    if filtre_statut:
        soumissions = soumissions.filter(statut=filtre_statut)
        soumissions_tdtp = soumissions_tdtp.filter(statut=filtre_statut)
    
    # Fusionner les deux listes selon le filtre
    if filtre_type == 'devoirs':
        toutes_soumissions = list(soumissions)
    elif filtre_type == 'tdtp':
        toutes_soumissions = list(soumissions_tdtp)
    else:
        # Fusionner et trier par date
        toutes_soumissions = sorted(
            list(soumissions) + list(soumissions_tdtp),
            key=lambda x: x.date_soumission,
            reverse=True
        )
    
    # Statistiques
    total_soumissions = len(toutes_soumissions)
    en_attente = sum(1 for s in toutes_soumissions if s.statut == 'EN_ATTENTE')
    soumises = sum(1 for s in toutes_soumissions if s.statut == 'SOUMIS')
    corrigees = sum(1 for s in toutes_soumissions if s.statut == 'CORRIGE')
    notees = sum(1 for s in toutes_soumissions if s.statut == 'NOTE')
    
    context = {
        'soumissions_devoirs': soumissions,
        'soumissions_tdtp': soumissions_tdtp,
        'toutes_soumissions': toutes_soumissions,
        'mes_cours': mes_cours,
        'filtre_cours': filtre_cours,
        'filtre_statut': filtre_statut,
        'filtre_type': filtre_type,
        'statistiques': {
            'total': total_soumissions,
            'en_attente': en_attente,
            'soumises': soumises,
            'corrigees': corrigees,
            'notees': notees,
        }
    }
    return render(request, 'academique/voir_devoirs_soumis.html', context)

@login_required
def evaluer_soumission(request, soumission_id):
    """Évaluer une soumission de devoir ou TD/TP"""
    if request.user.role != 'PROFESSEUR':
        return render(request, 'core/acces_interdit.html')
    
    # Essayer de trouver la soumission dans les deux modèles
    soumission = None
    type_soumission = None
    
    try:
        soumission = SoumissionDevoir.objects.get(id=soumission_id)
        # Vérifier que c'est le professeur de ce cours
        if soumission.devoir.cours.professeur_principal != request.user:
            return render(request, 'core/acces_interdit.html')
        type_soumission = 'DEVOIR'
    except SoumissionDevoir.DoesNotExist:
        try:
            soumission = SoumissionTDTP.objects.get(id=soumission_id)
            # Vérifier que c'est le professeur de ce cours
            if soumission.support_cours.cours.professeur_principal != request.user:
                return render(request, 'core/acces_interdit.html')
            type_soumission = 'TDTP'
        except SoumissionTDTP.DoesNotExist:
            return render(request, 'core/acces_interdit.html')
    
    if request.method == 'POST':
        note = request.POST.get('note')
        feedback = request.POST.get('feedback_professeur')
        statut = request.POST.get('statut')
        
        if note and statut:
            soumission.note = note
            soumission.feedback_professeur = feedback
            soumission.statut = statut
            soumission.save()
            messages.success(request, "Soumission évaluée avec succès !")
        
        return redirect('voir_devoirs_soumis')
    
    return redirect('voir_devoirs_soumis')

@login_required
def dashboard_chef(request):
    # 1. Identifier le département géré par ce chef
    try:
        mon_departement = Departement.objects.get(chef=request.user)
    except Departement.DoesNotExist:
        # Si par erreur il arrive ici sans être chef
        messages.error(request, "Vous n'êtes responsable d'aucun département.")
        return redirect('dashboard_prof')

    # 2. Récupérer uniquement les données de CE département
    # Les filières de ce département
    filieres = mon_departement.filieres_academiques.all()
    
    # Les cours liés à ces filières
    cours = Cours.objects.filter(filiere__in=filieres)
    
    # Les professeurs qui travaillent dans ce département (via les cours)
    # .distinct() évite les doublons si un prof a plusieurs cours
    profs_ids = cours.values_list('professeur_principal', flat=True)
    nb_profs = User.objects.filter(id__in=profs_ids).count()

    context = {
        'departement': mon_departement,
        'nb_filieres': filieres.count(),
        'nb_cours': cours.count(),
        'nb_profs': nb_profs,
        'derniers_cours': cours.order_by('-id')[:5]
    }
    return render(request, 'academique/dashboard_chef.html', context)

@login_required
def gerer_cours_departement(request):
    # 1. Vérifier si c'est un Chef
    try:
        dept = Departement.objects.get(chef=request.user)
    except Departement.DoesNotExist:
        return redirect('dashboard_prof')

    # 2. Gestion du formulaire d'ajout
    if request.method == 'POST':
        form = CoursForm(request.POST)
        if form.is_valid():
            # Sécurité : On vérifie que la filière choisie appartient bien au département du chef
            cours = form.save(commit=False)
            if cours.filiere.departement == dept:
                cours.save()
                messages.success(request, "Cours ajouté avec succès.")
            else:
                messages.error(request, "Erreur : Cette filière n'appartient pas à votre département.")
            return redirect('gerer_cours_chef')
    else:
        form = CoursForm()
        # Filtrer la liste des filières pour ne montrer que celles du département
        form.fields['filiere'].queryset = dept.filieres_academiques.all()

    # 3. Liste des cours existants du département
    cours_list = Cours.objects.filter(filiere__departement=dept).order_by('filiere', 'nom')

    context = {
        'departement': dept,
        'cours': cours_list,
        'form': form
    }
    return render(request, 'academique/liste_cours_chef.html', context)

@login_required
def planifier_seances_chef(request):
    try:
        dept = Departement.objects.get(chef=request.user)
    except Departement.DoesNotExist:
        return redirect('dashboard_prof')

    if request.method == 'POST':
        form = SeanceForm(request.POST)
        if form.is_valid():
            seance = form.save(commit=False)
            # Vérif sécurité : le cours doit appartenir au département
            if seance.cours.filiere.departement == dept:
                seance.save()
                messages.success(request, "Séance planifiée.")
            else:
                messages.error(request, "Ce cours n'est pas dans votre département.")
            return redirect('planifier_seances_chef')
    else:
        form = SeanceForm()
        # On ne propose que les cours du département dans la liste déroulante
        form.fields['cours'].queryset = Cours.objects.filter(filiere__departement=dept)

    # Liste des séances existantes (triées par jour)
    seances = Seance.objects.filter(cours__filiere__departement=dept).order_by('jour', 'heure_debut')
    
    return render(request, 'academique/planning_chef.html', {'seances': seances, 'form': form})






# ============ INTERFACE ETUDIANT ============

@login_required
def dashboard_etudiant(request):
    """Tableau de bord principal de l'étudiant"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
        mes_cours = Cours.objects.filter(filiere=dossier.filiere)
    except DossierEtudiant.DoesNotExist:
        mes_cours = []
    
    # Récupérer les derniers devoirs et notes
    notes_recentes = Note.objects.filter(etudiant=request.user).order_by('-date_saisie')[:5]
    devoirs = Devoir.objects.filter(cours__in=mes_cours, statut='ACTIF').order_by('date_limite')
    documents = DemandeDocument.objects.filter(etudiant=request.user).order_by('-date_creation')
    annonces = Annonce.objects.filter(
        cible__in=['TOUS', 'ETUDIANTS']
    ).order_by('-important', '-date_publication')[:3] 
    context = {
        'dossier': dossier if 'dossier' in locals() else None,
        'mes_cours': mes_cours,
        'notes_recentes': notes_recentes,
        'devoirs_actifs': devoirs[:5],
        'documents': documents,
        'annonces': annonces,
    }
    return render(request, 'academique/dashboard_etudiant.html', context)

@login_required
def mes_notes(request):
    """Consulter ses notes"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    notes = Note.objects.filter(etudiant=request.user).select_related('cours').order_by('-date_saisie')
    
    # Calculer la moyenne par cours
    notes_par_cours = {}
    for note in notes:
        if note.cours.id not in notes_par_cours:
            notes_par_cours[note.cours.id] = {
                'cours': note.cours,
                'notes': []
            }
        notes_par_cours[note.cours.id]['notes'].append(note)
    
    context = {
        'notes': notes,
        'notes_par_cours': notes_par_cours.values()
    }
    return render(request, 'academique/mes_notes.html', context)

@login_required
def mon_emploi_temps_etudiant(request):
    """Afficher l'emploi du temps de l'étudiant"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
        mes_cours = Cours.objects.filter(filiere=dossier.filiere)
        seances = Seance.objects.filter(cours__in=mes_cours).order_by('jour', 'heure_debut')
    except DossierEtudiant.DoesNotExist:
        seances = []
    
    # Trier par jour
    ordre_jours = {'LUNDI': 1, 'MARDI': 2, 'MERCREDI': 3, 'JEUDI': 4, 'VENDREDI': 5, 'SAMEDI': 6}
    seances = sorted(seances, key=lambda x: ordre_jours.get(x.jour, 7))
    
    context = {'seances': seances}
    return render(request, 'academique/emploi_temps_etudiant.html', context)

@login_required
def mes_reclamations(request):
    """Gérer ses réclamations en tant qu'étudiant"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    reclamations = Reclamation.objects.filter(etudiant=request.user).order_by('-date_creation')
    
    if request.method == 'POST':
        cours_id = request.POST.get('cours_id')
        message = request.POST.get('message')
        
        try:
            # Vérifier que l'étudiant suit ce cours
            dossier = DossierEtudiant.objects.get(etudiant=request.user)
            cours = get_object_or_404(Cours, id=cours_id, filiere=dossier.filiere)
            
            Reclamation.objects.create(
                etudiant=request.user,
                cours=cours,
                message=message,
                statut='EN_ATTENTE'
            )
            messages.success(request, "Votre réclamation a été enregistrée.")
            return redirect('mes_reclamations')
        except DossierEtudiant.DoesNotExist:
            messages.error(request, "Erreur : aucun dossier d'étudiant trouvé.")
            return redirect('mes_reclamations')
    
    # Récupérer les cours de l'étudiant pour le formulaire
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
        mes_cours = Cours.objects.filter(filiere=dossier.filiere)
    except DossierEtudiant.DoesNotExist:
        mes_cours = []
    
    context = {
        'reclamations': reclamations,
        'mes_cours': mes_cours,
    }
    return render(request, 'academique/mes_reclamations.html', context)

@login_required
def mes_devoirs(request):
    """Liste des devoirs à remettre (incluant TD et TP)"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
        mes_cours = Cours.objects.filter(filiere=dossier.filiere)
    except DossierEtudiant.DoesNotExist:
        mes_cours = []
    
    from .models import Devoir, SoumissionDevoir, SupportCours, SoumissionTDTP
    
    # Récupérer les devoirs
    devoirs = Devoir.objects.filter(cours__in=mes_cours, statut='ACTIF').order_by('date_limite')
    
    # Récupérer les supports TD/TP
    supports_tdtp = SupportCours.objects.filter(
        cours__in=mes_cours, 
        type_support__in=['TD', 'TP']
    ).order_by('date_ajout')
    
    # Ajouter l'état de soumission pour chaque devoir
    devoirs_avec_soumission = []
    for devoir in devoirs:
        try:
            soumission = SoumissionDevoir.objects.get(devoir=devoir, etudiant=request.user)
        except SoumissionDevoir.DoesNotExist:
            soumission = None
        devoirs_avec_soumission.append({
            'type': 'DEVOIR',
            'devoir': devoir,
            'soumission': soumission
        })
    
    # Ajouter l'état de soumission pour chaque TD/TP
    supports_tdtp_avec_soumission = []
    for support in supports_tdtp:
        try:
            soumission = SoumissionTDTP.objects.get(support_cours=support, etudiant=request.user)
        except SoumissionTDTP.DoesNotExist:
            soumission = None
        supports_tdtp_avec_soumission.append({
            'type': 'TDTP',
            'support': support,
            'soumission': soumission
        })
    
    # Fusionner et trier
    tous_les_travaux = devoirs_avec_soumission + supports_tdtp_avec_soumission
    
    context = {
        'devoirs_avec_soumission': devoirs_avec_soumission,
        'supports_tdtp_avec_soumission': supports_tdtp_avec_soumission,
        'tous_les_travaux': tous_les_travaux,
    }
    return render(request, 'academique/mes_devoirs.html', context)

@login_required
def soumettre_devoir(request, devoir_id):
    """Soumettre un devoir"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    from .models import Devoir, SoumissionDevoir
    from .forms import SoumissionDevoirForm
    
    devoir = get_object_or_404(Devoir, id=devoir_id)
    
    # Vérifier que l'étudiant suit le cours
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
        if devoir.cours.filiere != dossier.filiere:
            return render(request, 'core/acces_interdit.html')
    except DossierEtudiant.DoesNotExist:
        return render(request, 'core/acces_interdit.html')
    
    soumission, created = SoumissionDevoir.objects.get_or_create(
        devoir=devoir, 
        etudiant=request.user
    )
    
    if request.method == 'POST':
        form = SoumissionDevoirForm(request.POST, request.FILES, instance=soumission)
        if form.is_valid():
            soumission = form.save(commit=False)
            soumission.devoir = devoir
            soumission.etudiant = request.user
            soumission.statut = 'SOUMIS'
            soumission.date_soumission = timezone.now()
            soumission.save()
            messages.success(request, "Devoir soumis avec succès !")
            return redirect('mes_devoirs')
    else:
        form = SoumissionDevoirForm(instance=soumission)
    
    context = {
        'devoir': devoir,
        'soumission': soumission,
        'form': form,
    }
    return render(request, 'academique/soumettre_devoir.html', context)

@login_required
def profil_etudiant(request):
    """Profil de l'étudiant avec édition et changement de mot de passe"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
    except DossierEtudiant.DoesNotExist:
        dossier = None
    
    # Initialisation des formulaires
    user_form = StudentProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        # CAS 1 : Mise à jour des infos personnelles
        if 'update_profile' in request.POST:
            user_form = StudentProfileForm(request.POST, request.FILES, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Vos informations ont été mises à jour avec succès.")
                return redirect('profil_etudiant')
        
        # CAS 2 : Changement de mot de passe
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Important : maintient l'utilisateur connecté après le changement
                update_session_auth_hash(request, user)
                messages.success(request, "Votre mot de passe a été modifié.")
                return redirect('profil_etudiant')
            else:
                messages.error(request, "Erreur dans le changement de mot de passe. Vérifiez les champs.")

    context = {
        'user': request.user,
        'dossier': dossier,
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'academique/profil_etudiant.html', context)

@login_required
def reclamation_note(request, note_id):
    """Créer une réclamation directement depuis une note"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    note = get_object_or_404(Note, id=note_id, etudiant=request.user)
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        # Vérifier s'il existe déjà une réclamation pour cette note/cours
        reclamation_existante = Reclamation.objects.filter(
            etudiant=request.user,
            cours=note.cours,
            statut='EN_ATTENTE'
        ).exists()
        
        if reclamation_existante:
            messages.warning(request, "Vous avez déjà une réclamation en attente pour ce cours.")
        else:
            Reclamation.objects.create(
                etudiant=request.user,
                cours=note.cours,
                message=message,
                statut='EN_ATTENTE'
            )
            messages.success(request, "Votre réclamation a été enregistrée avec succès.")
            return redirect('mes_reclamations')
    
    context = {
        'note': note,
    }
    return render(request, 'academique/reclamation_note.html', context)

@login_required
def supports_cours_etudiant(request):
    """Afficher les supports pour un cours spécifique sélectionné"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    # 1. On récupère l'ID du cours depuis l'URL (ex: ?cours=12)
    cours_id = request.GET.get('cours')
    
    # Si pas d'ID, on renvoie au dashboard (sécurité)
    if not cours_id:
        from django.contrib import messages
        messages.warning(request, "Veuillez sélectionner un cours pour voir ses supports.")
        return redirect('dashboard_etudiant')
    
    # 2. On vérifie que l'étudiant a le droit de voir ce cours
    cours = get_object_or_404(Cours, id=cours_id)
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
        if cours.filiere != dossier.filiere:
            return render(request, 'core/acces_interdit.html')
    except DossierEtudiant.DoesNotExist:
        return render(request, 'core/acces_interdit.html')
    
    # 3. On récupère la liste plate des supports (C'est ce que le template attend !)
    supports = SupportCours.objects.filter(cours=cours).order_by('-date_ajout')
    
    context = {
        'cours': cours,       # Pour l'en-tête (Nom du cours, Prof...)
        'supports': supports, # La liste pour la grille
    }
    return render(request, 'academique/supports_cours_etudiant.html', context)

@login_required
def soumettre_tdtp(request, support_id):
    """Soumettre une réponse pour un TD ou TP"""
    if request.user.role != 'ETUDIANT':
        return render(request, 'core/acces_interdit.html')
    
    from .models import SupportCours, SoumissionTDTP
    
    support = get_object_or_404(
        SupportCours, 
        id=support_id, 
        type_support__in=['TD', 'TP']
    )
    
    # Vérifier que l'étudiant suit le cours
    try:
        dossier = DossierEtudiant.objects.get(etudiant=request.user)
        if support.cours.filiere != dossier.filiere:
            return render(request, 'core/acces_interdit.html')
    except DossierEtudiant.DoesNotExist:
        return render(request, 'core/acces_interdit.html')
    
    soumission, created = SoumissionTDTP.objects.get_or_create(
        support_cours=support, 
        etudiant=request.user
    )
    
    if request.method == 'POST':
        fichier = request.FILES.get('fichier')
        format_fichier = request.POST.get('format_fichier', 'PDF')
        commentaire = request.POST.get('commentaire', '')
        
        if fichier:
            soumission.fichier = fichier
            soumission.format_fichier = format_fichier
            soumission.commentaire = commentaire
            soumission.statut = 'SOUMIS'
            soumission.date_soumission = timezone.now()
            soumission.save()
            messages.success(request, "Votre réponse a été soumise avec succès !")
            return redirect('mes_devoirs')
        else:
            messages.error(request, "Veuillez sélectionner un fichier.")
    
    context = {
        'support': support,
        'soumission': soumission,
        'formats': SoumissionTDTP.FORMATS_ACCEPTES,
    }
    return render(request, 'academique/soumettre_tdtp.html', context)

@login_required
def upload_notes_cours(request, cours_id):
    """
    Permet au professeur d'envoyer un fichier de notes (Excel/PDF)
    au lieu de saisir manuellement.
    """
    # 1. On récupère le cours et on vérifie que c'est bien le prof de ce cours
    cours = get_object_or_404(Cours, id=cours_id, professeur_principal=request.user)
    
    if request.method == "POST":
        fichier_recu = request.FILES.get('fichier')
        
        if fichier_recu:
            # 2. On crée l'entrée dans la table de la Scolarité
            FichierNotes.objects.create(
                professeur=request.user,
                matiere=cours.nom,
                fichier=fichier_recu,
                etat='EN_ATTENTE'
            )
            messages.success(request, f"Le fichier pour {cours.nom} a été envoyé à la scolarité !")
        else:
            messages.error(request, "Erreur : Veuillez sélectionner un fichier.")
            
    # 3. On recharge la page de saisie des notes
    return redirect('saisie_notes', cours_id=cours.id)
@login_required
def demander_document(request):
    if request.user.role != 'ETUDIANT':
        return redirect('home')

    if request.method == "POST":
        type_doc = request.POST.get('type_document')
        
        # Vérifier si une demande est déjà en cours
        existe = DemandeDocument.objects.filter(
            etudiant=request.user, 
            type_document=type_doc, 
            statut='DEMANDE'
        ).exists()
        
        if existe:
            messages.warning(request, "Vous avez déjà une demande en cours pour ce document.")
        else:
            DemandeDocument.objects.create(
                etudiant=request.user,
                type_document=type_doc,
                statut='DEMANDE'
            )
            messages.success(request, "Votre demande a été envoyée à la scolarité.")
    
    return redirect('dashboard_etudiant')



# ============ INTERFACE Administration ============
@login_required
def dashboard_direction(request):
    """Tableau de bord global"""
    if request.user.role != 'ADMIN':
        return render(request, 'core/acces_interdit.html')
    
    # Statistiques
    stats = {
        'nb_etudiants': User.objects.filter(role='ETUDIANT').count(),
        'nb_profs': User.objects.filter(role='PROFESSEUR').count(),
        'nb_filieres': Filiere.objects.count(),
        'nb_annonces': Annonce.objects.count(),
    }
    
    # Dernières annonces publiées
    annonces = Annonce.objects.filter(auteur=request.user).order_by('-date_publication')[:5]
    
    return render(request, 'academique/dashboard_direction.html', {'stats': stats, 'annonces': annonces})

@login_required
def gerer_filieres_direction(request):
    """Liste et ajout de filières"""
    if request.user.role != 'ADMIN':
        return render(request, 'core/acces_interdit.html')

    if request.method == 'POST':
        form = FiliereForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nouvelle filière créée avec succès !")
            return redirect('gerer_filieres_direction')
    else:
        form = FiliereForm()
    
    filieres = Filiere.objects.select_related('departement', 'cycle').all()
    
    return render(request, 'academique/gerer_filieres.html', {'filieres': filieres, 'form': form})

@login_required
def gerer_annonces_direction(request):
    """Publier des annonces"""
    if request.user.role != 'ADMIN':
        return render(request, 'core/acces_interdit.html')

    if request.method == 'POST':
        form = AnnonceForm(request.POST)
        if form.is_valid():
            annonce = form.save(commit=False)
            annonce.auteur = request.user
            annonce.save()
            messages.success(request, "Annonce publiée.")
            return redirect('gerer_annonces_direction')
    else:
        form = AnnonceForm()
    
    annonces = Annonce.objects.filter(auteur=request.user).order_by('-date_publication')
    
    return render(request, 'academique/gerer_annonces.html', {'annonces': annonces, 'form': form})

@login_required
def profil_direction(request):
    """Gestion du profil pour la Direction"""
    if request.user.role != 'ADMIN': # Rappel : Votre clé BDD est 'ADMIN'
        return render(request, 'core/acces_interdit.html')

    user = request.user
    
    # Initialisation des formulaires
    user_form = StudentProfileForm(instance=user)
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        # CAS 1 : Mise à jour des infos (Photo, Nom...)
        if 'update_profile' in request.POST:
            user_form = StudentProfileForm(request.POST, request.FILES, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profil mis à jour avec succès.")
                return redirect('profil_direction')
        
        # CAS 2 : Changement de mot de passe
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # Garde la session active
                messages.success(request, "Votre mot de passe a été modifié.")
                return redirect('profil_direction')
            else:
                messages.error(request, "Erreur dans le mot de passe. Vérifiez les règles de sécurité.")

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'academique/profil_direction.html', context)