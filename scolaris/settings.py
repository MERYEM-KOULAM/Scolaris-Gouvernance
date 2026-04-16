import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-votre-cle-secrete-ici-pour-dev'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jazzmin',
    # --- NOS APPLICATIONS MÉTIERS (Séparées proprement) ---
    'core',         # Gestion des utilisateurs (Personnes)
    'rh',           # Gestion des contrats et départements
    'academique',   # Gestion des cours, filières, cycles
    'scolarite',    # Gestion des inscriptions et dossiers étudiants
    'evaluation',   # Gestion des notes et audit
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scolaris.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Dossier global pour vos templates HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scolaris.wsgi.application'

# Database
# Utilisation de SQLite comme demandé
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr' # On met le site en Français
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files (Pour les uploads de photos, devoirs, justificatifs)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- CONFIGURATION ESSENTIELLE ---
# On dit à Django d'utiliser NOTRE modèle utilisateur défini dans 'core'
AUTH_USER_MODEL = 'core.User'

# Redirection après connexion/déconnexion
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# À la fin de settings.py

# L'URL qui sera utilisée dans le navigateur (ex: /media/mon_fichier.pdf)
MEDIA_URL = '/media/'

# Le dossier physique sur votre ordinateur où les fichiers sont stockés
import os
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

JAZZMIN_SETTINGS = {
    # Titre de la fenêtre
    "site_title": "Administration Scolaris",
    "site_header": "Scolaris Admin",
    "site_brand": "Scolaris",
    
    # Message de bienvenue sur l'écran de login
    "welcome_sign": "Bienvenue dans l'administration système",

    # Copyright en bas de page
    "copyright": "Scolaris Ltd",
    
    # Menu latéral
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Icônes pour vos applications (facultatif, utilise FontAwesome)
    "icons": {
        "auth": "fas fa-users-cog",
        "core.user": "fas fa-user",
        "academique.cours": "fas fa-book",
        "academique.filiere": "fas fa-graduation-cap",
        "rh.departement": "fas fa-building",
    },
}

# Thème visuel (Couleurs)
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",   # Essayez aussi "journal", "darkly", "simplex"
    #"dark_mode_theme": "darkly", # Activer le mode sombre automatique
}