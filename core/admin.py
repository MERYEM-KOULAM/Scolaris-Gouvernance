# Dans core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    # On ajoute nos champs personnalisés aux fieldsets existants
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Complémentaires', {'fields': ('role', 'photo_profil', 'adresse')}),
    )
    # Pareil pour la page de création
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Complémentaires', {'fields': ('role', 'photo_profil', 'adresse')}),
    )
    
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser']

admin.site.register(User, CustomUserAdmin)