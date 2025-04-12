from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/service/', include('service_management.urls')),
    path('api/auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),
    path('api/user/', include('user_profile.urls')),
    path('api/article/', include('article.urls')),
    path('api/activity/', include('activity.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
