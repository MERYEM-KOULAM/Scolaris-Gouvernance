from django import forms
from .models import SupportCours, SoumissionDevoir
from .models import Cours, Seance
from django.contrib.auth import get_user_model
from .models import Annonce, Filiere

class SupportCoursForm(forms.ModelForm):
    class Meta:
        model = SupportCours
        fields = ['titre', 'type_support', 'fichier']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Chapitre 1 - Introduction'}),
            'type_support': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['code', 'nom', 'volume_horaire', 'filiere', 'semestre', 'professeur_principal']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'volume_horaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-select'}),
            'semestre': forms.NumberInput(attrs={'class': 'form-control'}),
            'professeur_principal': forms.Select(attrs={'class': 'form-select'}),
        }

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['cours', 'jour', 'heure_debut', 'heure_fin', 'salle']
        widgets = {
            'cours': forms.Select(attrs={'class': 'form-select'}),
            'jour': forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'salle': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SoumissionDevoirForm(forms.ModelForm):
    class Meta:
        model = SoumissionDevoir
        fields = ['fichier', 'commentaire']
        widgets = {
            'fichier': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.zip'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ajoutez un commentaire (optionnel)'}),
        }


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'photo_profil'] # Ajoutez 'photo_profil' si votre modèle User l'a
        # Sinon juste : fields = ['first_name', 'last_name', 'email']

class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = ['titre', 'contenu', 'cible', 'important']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet de l\'annonce'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cible': forms.Select(attrs={'class': 'form-select'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FiliereForm(forms.ModelForm):
    class Meta:
        model = Filiere
        fields = ['nom', 'cycle', 'departement', 'responsable']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Génie Logiciel'}),
            'cycle': forms.Select(attrs={'class': 'form-select'}),
            'departement': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }