from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .forms import CandidatureForm
from django.contrib.auth.hashers import make_password

# Import des modèles
from core.models import User
# Modifiez cette ligne en haut de scolarite/views.py :
from .models import DemandeInscription, DemandeDocument, DossierEtudiant, Note, FichierNotes

# --- FONCTION DE TEST (PERMISSIONS) ---
def is_scolarite(user):
    return user.role == 'SCOLARITE' or user.is_superuser

# --- DASHBOARD ---
@login_required
@user_passes_test(is_scolarite)
def dashboard(request):
    # 1. Chiffres clés
    nb_etudiants = User.objects.filter(role='ETUDIANT').count()
    inscriptions_attente = DemandeInscription.objects.filter(statut='EN_ATTENTE').count()
    docs_a_traiter = DemandeDocument.objects.filter(statut='DEMANDE').count()
    fichiers_notes_attente = FichierNotes.objects.filter(etat='EN_ATTENTE').count()
    
    # 2. Dernières demandes
    dernieres_demandes = DemandeInscription.objects.filter(statut='EN_ATTENTE').order_by('-date_demande')[:5]

    context = {
        'nb_etudiants': nb_etudiants,
        'inscriptions_attente': inscriptions_attente,
        'docs_a_traiter': docs_a_traiter,
        'fichiers_notes_attente': fichiers_notes_attente,
        'dernieres_demandes': dernieres_demandes
    }
    return render(request, 'scolarite/dashboard_scolarite.html', context)

# --- GESTION DES INSCRIPTIONS ---
@login_required
@user_passes_test(is_scolarite)
def liste_inscriptions(request):
    demandes = DemandeInscription.objects.filter(statut='EN_ATTENTE').order_by('-date_demande')
    return render(request, 'scolarite/liste_inscriptions.html', {'demandes': demandes})

@login_required
@user_passes_test(is_scolarite)
def traiter_inscription(request, id_demande, decision):
    demande = get_object_or_404(DemandeInscription, id=id_demande)
    
    if decision == 'accepter':
        demande.statut = 'ACCEPTEE'
        demande.save()
        
        candidat = demande.candidat
        candidat.role = 'ETUDIANT'
        candidat.save()
        
        DossierEtudiant.objects.create(
            etudiant=candidat,
            filiere=demande.filiere_souhaitee,
            date_entree=date.today(),
            annee_actuelle="1ère année"
        )
        messages.success(request, f"L'étudiant {candidat} a été inscrit avec succès !")
        
    elif decision == 'refuser':
        demande.statut = 'REFUSEE'
        demande.save()
        messages.warning(request, f"La demande de {demande.candidat} a été refusée.")
        
    return redirect('scolarite:liste_inscriptions')

# --- GESTION DES ÉTUDIANTS (ANNUAIRE) ---
@login_required
@user_passes_test(is_scolarite)
def liste_etudiants(request):
    query = request.GET.get('q')
    etudiants = User.objects.filter(role='ETUDIANT').select_related('dossier_scolaire')
    
    if query:
        etudiants = etudiants.filter(
            Q(last_name__icontains=query) | 
            Q(first_name__icontains=query) |
            Q(email__icontains=query)
        )
        
    return render(request, 'scolarite/liste_etudiants.html', {'etudiants': etudiants})

@login_required
@user_passes_test(is_scolarite)
def voir_dossier(request, pk):
    etudiant = get_object_or_404(User, pk=pk, role='ETUDIANT')
    
    # --- C'EST CETTE LIGNE QUI MANQUAIT ---
    documents = DemandeDocument.objects.filter(etudiant=etudiant).order_by('-date_creation')
    
    return render(request, 'scolarite/dossier_etudiant.html', {
        'etudiant': etudiant,
        'documents': documents  # Et on l'ajoute ici
    })

# --- GESTION DES DOCUMENTS (C'était ça qui manquait !) ---
@login_required
@user_passes_test(is_scolarite)
def liste_documents(request):
    demandes = DemandeDocument.objects.exclude(statut='PRET').order_by('date_creation')
    return render(request, 'scolarite/liste_documents.html', {'demandes': demandes})

@login_required
@user_passes_test(is_scolarite)
def traiter_document(request, id_doc):
    doc = get_object_or_404(DemandeDocument, id=id_doc)
    doc.statut = 'PRET'
    doc.save()
    messages.success(request, f"Le document pour {doc.etudiant} est marqué comme PRÊT.")
    return redirect('scolarite:liste_documents')
# Dans scolarite/views.py

@login_required
@user_passes_test(is_scolarite)
def admin_creer_document(request, etudiant_id):
    if request.method == "POST":
        etudiant = get_object_or_404(User, pk=etudiant_id)
        type_doc = request.POST.get('type_document')
        
        # On crée le document
        DemandeDocument.objects.create(
            etudiant=etudiant,
            type_document=type_doc,
            statut='PRET' # On le met directement en PRET car c'est l'admin qui l'ajoute
        )
        
        messages.success(request, f"Le document ({type_doc}) a été ajouté au dossier.")
        return redirect('scolarite:voir_dossier', pk=etudiant_id)
    
    return redirect('scolarite:liste_etudiants')
# Dans scolarite/views.py

@login_required
def profil_scolarite(request):
    """ Affiche le profil de l'agent connecté """
    return render(request, 'scolarite/mon_profil.html')
# À ajouter tout en bas de scolarite/views.py

@login_required
@user_passes_test(is_scolarite)
def ajouter_note(request, etudiant_id):
    # On récupère l'étudiant concerné
    etudiant = get_object_or_404(User, pk=etudiant_id)
    
    if request.method == "POST":
        # On récupère les données du formulaire
        matiere = request.POST.get('matiere')
        valeur = request.POST.get('valeur')
        semestre = request.POST.get('semestre')
        
        # On enregistre la note dans la base de données
        Note.objects.create(
            etudiant=etudiant,
            matiere=matiere,
            valeur=valeur,
            semestre=semestre
        )
        
        messages.success(request, f"Note de {matiere} ajoutée avec succès.")
        # On recharge la page du dossier pour voir la nouvelle note
        return redirect('scolarite:voir_dossier', pk=etudiant_id)
    
    # Si ce n'est pas un POST, on renvoie vers la liste
    return redirect('scolarite:liste_etudiants')
# À la fin de scolarite/views.py

from .models import FichierNotes # Assurez-vous que l'import est là haut

@login_required
@user_passes_test(is_scolarite)
def liste_notes_profs(request):
    # On récupère les fichiers en attente
    fichiers = FichierNotes.objects.filter(etat='EN_ATTENTE').order_by('-date_envoi')
    return render(request, 'scolarite/reception_notes.html', {'fichiers': fichiers})

@login_required
@user_passes_test(is_scolarite)
def traiter_fichier_prof(request, id_fichier):
    fichier = get_object_or_404(FichierNotes, id=id_fichier)
    fichier.etat = 'TRAITE'
    fichier.save()
    messages.success(request, f"Le fichier de {fichier.matiere} a été archivé.")
    return redirect('scolarite:liste_notes_profs')
def importer_document(request, demande_id):
    """Permet à la scolarité d'envoyer le fichier PDF à l'étudiant"""
    demande = get_object_or_404(DemandeDocument, id=demande_id)

    if request.method == 'POST':
        fichier = request.FILES.get('fichier')
        if fichier:
            demande.fichier = fichier
            demande.statut = 'PRET'  # On change le statut automatiquement
            demande.save()
            messages.success(request, f"Document envoyé à {demande.etudiant.first_name} !")
        else:
            messages.error(request, "Veuillez sélectionner un fichier.")
    
    # CORRECTION ICI : On redirige vers 'scolarite:liste_documents'
    return redirect('scolarite:liste_documents')
def page_candidature(request):
    """ Page publique pour que les candidats s'inscrivent """
    if request.method == 'POST':
        form = CandidatureForm(request.POST)
        if form.is_valid():
            # 1. On crée d'abord l'Utilisateur (CANDIDAT)
            user = User.objects.create(
                username=form.cleaned_data['email'], # On utilise l'email comme login
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=make_password(form.cleaned_data['password']), # On crypte le mot de passe
                role='CANDIDAT', # Important : Il est candidat pour l'instant
                telephone=form.cleaned_data['telephone']
            )
            
            # 2. On crée la Demande d'inscription liée
            DemandeInscription.objects.create(
                candidat=user,
                filiere_souhaitee=form.cleaned_data['filiere'],
                message=form.cleaned_data['message'],
                statut='EN_ATTENTE'
            )
            
            # 3. Message de succès et redirection
            messages.success(request, "Votre candidature a été envoyée avec succès ! La scolarité va l'étudier.")
            return redirect('candidature_succes') # On le renvoie vers la page de succès
    else:
        form = CandidatureForm()

    return render(request, 'scolarite/page_candidature.html', {'form': form})
# 2. LA FONCTION QUI AFFICHE LA PAGE DE SUCCÈS (À AJOUTER JUSTE EN DESSOUS)
def candidature_succes(request):
    return render(request, 'scolarite/candidature_succes.html')
# Dans scolarite/views.py

@login_required
def dashboard_candidat(request):
    """ Espace personnel du candidat pour voir son statut """
    # Sécurité : On vérifie que c'est bien un candidat
    if request.user.role != 'CANDIDAT':
        return redirect('home')

    try:
        # On récupère sa demande
        demande = DemandeInscription.objects.get(candidat=request.user)
    except DemandeInscription.DoesNotExist:
        demande = None

    return render(request, 'scolarite/dashboard_candidat.html', {'demande': demande})