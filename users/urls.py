# users/urls.py
from django.urls import path
from .views import RegisterView
from .views import UserListView
from .views import user_profile
from .views import LoginView
from django.urls import path
from .views import UserProfileView, UpdateProfileView

urlpatterns = [
  
    path('register/', RegisterView.as_view(), name='register'),
    path('', UserListView.as_view(), name='user-list'),  # 👈 ajout de cette ligne
    path('login/', LoginView.as_view(), name='login'),
    # path('profile/', user_profile, name='user-profile'), 
    # path('profile/', UserDetailView.as_view(), name='user-profile'),
    path('profile/', UserProfileView.as_view(), name='user-profile'), 
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
]
