from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # <--- C'est lui le module important
from django.db.models import Q
from core.models import User
from .models import Departement, Contrat
from .forms import DepartementForm, EmployeForm, ContratForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from academique.forms import StudentProfileForm

# --- DASHBOARD ---
@login_required
def dashboard_rh(request):
    # Sécurité
    if request.user.role != 'RH' and not request.user.is_superuser:
        messages.error(request, "Accès refusé. Réservé au service RH.")
        return redirect('home') # Redirige vers la redirection intelligente

    # Stats
    total_profs = User.objects.filter(role='PROFESSEUR').count()
    total_etudiants = User.objects.filter(role='ETUDIANT').count()
    total_departements = Departement.objects.count()
    derniers_contrats = Contrat.objects.all().order_by('-date_debut')[:5]

    context = {
        'total_profs': total_profs,
        'total_etudiants': total_etudiants,
        'total_departements': total_departements,
        'derniers_contrats': derniers_contrats
    }
    return render(request, 'rh/dashboard_rh.html', context)

# --- LISTE DES EMPLOYÉS ---
@login_required
def liste_employes(request):
    if request.user.role != 'RH' and not request.user.is_superuser:
        return redirect('login')

    # On récupère Profs et RH
    employes = User.objects.filter(Q(role='PROFESSEUR') | Q(role='RH'))
    
    return render(request, 'rh/liste_employes.html', {'employes': employes})

# --- RECRUTEMENT (Création Compte) ---
@login_required
def recruter_employe(request):
    if request.user.role != 'RH' and not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            user = form.save()
            # C'est ici que ça bloquait : maintenant 'messages' fait bien référence au module
            messages.success(request, f"L'employé {user.username} a été recruté avec succès.")
            return redirect('liste_employes')
    else:
        form = EmployeForm()

    return render(request, 'rh/form_recrutement.html', {'form': form})

# --- GESTION DÉPARTEMENTS ---
@login_required
def liste_departements(request):
    if request.user.role != 'RH' and not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le département a été créé avec succès.")
            return redirect('liste_departements')
    else:
        form = DepartementForm()

    departements = Departement.objects.all().order_by('nom')
    context = {'departements': departements, 'form': form}
    return render(request, 'rh/liste_departements.html', context)

# --- NOUVEAU CONTRAT ---
@login_required
def nouveau_contrat(request):
    if request.user.role != 'RH' and not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        form = ContratForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le contrat a été signé et enregistré.")
            return redirect('dashboard_rh')
    else:
        form = ContratForm()

    return render(request, 'rh/form_contrat.html', {'form': form})

@login_required
def dossier_employe(request, employe_id):
    if request.user.role != 'RH' and not request.user.is_superuser:
        return redirect('login')
    
    # On récupère l'employé
    employe = get_object_or_404(User, id=employe_id)
    
    # On essaie de trouver son contrat (s'il en a un)
    # .first() permet d'éviter une erreur s'il n'en a pas
    contrat = Contrat.objects.filter(professeur=employe).first()
    
    context = {
        'employe': employe,
        'contrat': contrat
    }
    return render(request, 'rh/dossier_employe.html', context)

@login_required
def profil_rh(request):
    # Vérification du rôle
    if request.user.role != 'RH' and not request.user.is_superuser:
        return redirect('login')

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
                messages.success(request, "Vos informations ont été mises à jour.")
                return redirect('profil_rh')
        
        # CAS 2 : Changement de mot de passe
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # Garde la session active
                messages.success(request, "Votre mot de passe a été modifié avec succès.")
                return redirect('profil_rh')
            else:
                messages.error(request, "Erreur dans le changement de mot de passe.")

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'rh/profil_rh.html', context)