from django.urls import path
from .views import FavoriteListCreateView, FavoriteDeleteView

urlpatterns = [
    path('favorites/', FavoriteListCreateView.as_view(), name='favorites'),
    path('favorites/delete/<int:job_id>/', FavoriteDeleteView.as_view(), name='delete_favorite'),
]