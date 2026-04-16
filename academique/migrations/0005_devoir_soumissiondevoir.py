# Generated migration for Devoir and SoumissionDevoir models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academique', '0004_supportcours'),
    ]

    operations = [
        migrations.CreateModel(
            name='Devoir',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_limite', models.DateTimeField()),
                ('statut', models.CharField(choices=[('ACTIF', 'Actif'), ('TERMINE', 'Terminé'), ('ARCHVE', 'Archivé')], default='ACTIF', max_length=20)),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devoirs', to='academique.cours')),
            ],
        ),
        migrations.CreateModel(
            name='SoumissionDevoir',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='soumissions_devoirs/')),
                ('date_soumission', models.DateTimeField(auto_now_add=True)),
                ('commentaire', models.TextField(blank=True)),
                ('note', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('feedback_professeur', models.TextField(blank=True)),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('SOUMIS', 'Soumis'), ('CORRIGE', 'Corrigé'), ('NOTE', 'Noté')], default='EN_ATTENTE', max_length=20)),
                ('devoir', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soumissions', to='academique.devoir')),
                ('etudiant', models.ForeignKey(limit_choices_to={'role': 'ETUDIANT'}, on_delete=django.db.models.deletion.CASCADE, related_name='soumissions_devoirs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='soumissiondevoir',
            constraint=models.UniqueConstraint(fields=('devoir', 'etudiant'), name='soumissiondevoir_unique_devoir_etudiant'),
        ),
    ]
