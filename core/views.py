from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from rh.models import Departement
from .models import Annonce

@login_required
def home_redirect(request):
    user = request.user
    # --- AJOUT TEMPORAIRE POUR DÉBOGUER ---
    print("--------------------------------------------------")
    print(f"UTILISATEUR: {user.username}")
    print(f"RÔLE ENREGISTRÉ (Clé): '{user.role}'")  # C'est cette valeur qu'il faut copier
    print("--------------------------------------------------")
    # ---------------------------------------
    # Vérifier si c'est un Chef de Département
    # On regarde si cet utilisateur est listé comme 'chef' dans un département
    est_chef = Departement.objects.filter(chef=user).exists()

    if est_chef:
        return redirect('dashboard_chef') # On va créer cette vue
        
    elif user.role == 'PROFESSEUR':
        return redirect('dashboard_prof')
        
    elif user.role == 'RH':
        return redirect('dashboard_rh')
    elif request.user.role == 'SCOLARITE':
        return redirect('scolarite:dashboard')
        
    elif user.role == 'ETUDIANT':
        return redirect('dashboard_etudiant')
    elif user.role == 'CANDIDAT':
        # On le redirige vers le dashboard qu'on vient de créer dans l'app scolarite
        return redirect('scolarite:dashboard_candidat')
    
    elif user.role == 'ADMIN':
        return redirect('dashboard_direction')   
    
    elif user.is_superuser:
        return redirect('/admin/')
        
    return redirect('login')