from rest_framework import serializers, generics
from .models import Job
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination

# Serializer for the job model
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

# Filter class for job listings
class JobFilter(filters.FilterSet):
    titre = filters.CharFilter(field_name="titre", lookup_expr='icontains', label='Titre')  # Filter by title
    localisation = filters.CharFilter(field_name="localisation", lookup_expr='icontains', label='Localisation')  # Filter by location

    class Meta:
        model = Job
        fields = ['titre', 'localisation']

# Pagination class to handle paginated responses
class JobPagination(PageNumberPagination):
    page_size = 10  # Number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Max page size limit

# View for listing and creating job offers with pagination and filtering
class JobListCreateAPIView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = JobFilter
    pagination_class = JobPagination  # Add pagination class


from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'read', 'created_at', 'link']