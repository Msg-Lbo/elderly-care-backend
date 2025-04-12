from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'card-package', views.CardPackageViewSet, basename='card-package')
router.register(r'health-schedules', views.HealthScheduleViewSet, basename='health-schedule')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile-update'),
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    path('guardianship/', views.GuardianshipView.as_view(), name='guardiansh    ip'),
    path('guardianship/<int:pk>/', views.GuardianshipView.as_view(), name='guardianship-detail'),
    path('user/<int:user_id>/card-package/', views.UserCardPackageView.as_view(), name='user-card-package'),
    path('cards/', views.CardListView.as_view(), name='card-list'),
    path('cards/<int:card_id>/', views.CardDetailView.as_view(), name='card-detail'),
    path('guardianship/user/<int:user_id>/', views.GuardianshipView.as_view(), name='user-guardianship'),
    path('guardianship/ward/<int:ward_id>/', views.GuardianshipView.as_view(), name='ward-guardianship'),
    path('profiles/', views.ProfileView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
]
