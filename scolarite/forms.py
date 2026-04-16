from django import forms
from core.models import User
from .models import DemandeInscription
from academique.models import Filiere

class CandidatureForm(forms.ModelForm):
    # Champs pour créer l'utilisateur
    first_name = forms.CharField(label="Prénom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Nom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    telephone = forms.CharField(label="Téléphone", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Champ pour choisir la filière
    filiere = forms.ModelChoiceField(
        queryset=Filiere.objects.all(),
        label="Filière souhaitée",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Champ pour le message/motivation
    message = forms.CharField(
        label="Message / Motivation", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = DemandeInscription
        fields = ['filiere', 'message']