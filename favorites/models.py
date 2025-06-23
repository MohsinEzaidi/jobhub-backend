# favorites/models.py

from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job  # ou selon ton app
from django.conf import settings


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'job')  # empêche doublons
