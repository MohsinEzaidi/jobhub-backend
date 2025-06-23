# jobs/models.py
from django.db import models

class Job(models.Model):
    titre = models.CharField(max_length=200)
    entreprise = models.CharField(max_length=200)
    localisation = models.CharField(max_length=200)
    description = models.TextField()
    date_publication = models.DateField()
    date_limite = models.DateField()
    postes_disponibles = models.IntegerField()
    lien = models.URLField()
    secteur = models.CharField(max_length=200)
    fonction = models.CharField(max_length=200)
    experience = models.CharField(max_length=100)
    niveau_etudes = models.CharField(max_length=50)
    contrat = models.CharField(max_length=50)
    teletravail = models.CharField(max_length=50)
    # salary = models.CharField(max_length=100, blank=True, null=True)  # Add this
    # job_type = models.CharField(max_length=50, blank=True, null=True)  # Add this
    # experience = models.CharField(max_length=50, blank=True, null=True)  # Add this

    def __str__(self):
        return self.titre


from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.id} - {self.message[:20]}"  # Use ID instead of username/email
