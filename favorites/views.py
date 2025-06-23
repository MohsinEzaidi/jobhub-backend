from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Favorite
from jobs.models import Job
from .serializers import FavoriteSerializer

class FavoriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)


class FavoriteListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        job_id = request.data.get("job_id")
        try:
            job = Job.objects.get(id=job_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, job=job)
            return Response(FavoriteSerializer(favorite).data, status=201)
        except Job.DoesNotExist:
            return Response({"error": "Offre non trouvée"}, status=404)


class FavoriteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, job_id):
        favorite = Favorite.objects.filter(user=request.user, job__id=job_id).first()
        if favorite:
            favorite.delete()
            return Response({"message": "Favori supprimé"})
        return Response({"error": "Favori non trouvé"}, status=404)
