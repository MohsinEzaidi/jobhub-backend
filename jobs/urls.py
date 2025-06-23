from django.urls import path
from .views import (
    JobListView,
    JobDetailAPIView,
    NotificationList,
    MarkNotificationAsRead
)

urlpatterns = [
    # Job endpoints
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', JobDetailAPIView.as_view(), name='job-detail'),
    
    # Notification endpoints
    path('notifications/', NotificationList.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', MarkNotificationAsRead.as_view(), name='mark-notification-read'),
]