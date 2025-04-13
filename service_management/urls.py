from django.urls import path
from .views import ServiceListView, ServiceCreateView, ServiceDetailView, ServiceUpdateView, ServiceDeleteView

urlpatterns = [
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/create/', ServiceCreateView.as_view(), name='service-create'),
    path('services/<int:id>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/update/', ServiceUpdateView.as_view(), name='service-update'),
    path('services/delete/', ServiceDeleteView.as_view(), name='service-delete'),
]
