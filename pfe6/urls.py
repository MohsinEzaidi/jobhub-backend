from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include all API endpoints under single api/ namespace
    path('api/', include([
        path('', include('jobs.urls')),
        path('', include('users.urls')),
        path('', include('favorites.urls')),
        path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    ])),
]