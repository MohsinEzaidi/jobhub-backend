from rest_framework import generics, permissions
from .models import Job, Notification
from .serializers import JobSerializer, NotificationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication

class JobFilter(filters.FilterSet):
    titre = filters.CharFilter(lookup_expr='icontains')
    localisation = filters.CharFilter(lookup_expr='icontains')
    # Add remote filter
    teletravail = filters.BooleanFilter()
    # Add experience filter
    experience = filters.CharFilter(lookup_expr='iexact')
    # Add contract type filter
    contrat = filters.CharFilter(lookup_expr='iexact')
    # Add salary range filter
    salary_min = filters.NumberFilter(field_name='salaire', lookup_expr='gte')
    salary_max = filters.NumberFilter(field_name='salaire', lookup_expr='lte')

    class Meta:
        model = Job
        fields = ['titre', 'localisation', 'teletravail', 'experience', 'contrat']

class JobListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter
    # Add ordering
    ordering_fields = ['date_publication', 'salaire']
    ordering = ['-date_publication']

class JobDetailAPIView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

# Notification views remain unchanged

# At the bottom of the file
class NotificationList(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]  # Add JWT auth
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class MarkNotificationAsRead(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.instance.read = True
        serializer.save()