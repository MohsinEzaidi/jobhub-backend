# favorites/serializers.py

from rest_framework import serializers
from .models import Favorite
from jobs.serializers import JobSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    job = JobSerializer()  # pour afficher les infos du job

    class Meta:
        model = Favorite
        fields = ['id', 'job']
