from django import forms
from .models import Departement, Contrat
from core.models import User
from django.contrib.auth.forms import UserCreationForm

class DepartementForm(forms.ModelForm):
    chef = forms.ModelChoiceField(
        queryset=User.objects.filter(role='PROFESSEUR'),
        required=False,
        label="Chef de Département",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Departement
        fields = ['nom', 'description', 'chef']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EmployeForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'telephone']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ContratForm(forms.ModelForm):
    # CORRECTION ICI : On utilise le nom 'professeur' pour correspondre à la base de données
    professeur = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['PROFESSEUR', 'RH']),
        label="Employé",  # On garde l'étiquette "Employé" pour l'affichage
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Contrat
        # CORRECTION ICI : On liste 'professeur' au lieu de 'employe'
        fields = ['professeur', 'type_contrat', 'date_debut', 'date_fin', 'salaire_mensuel']
        widgets = {
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salaire_mensuel': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
        }