from django.urls import path
from . import views
from .views import ProjectView

urlpatterns = [
    path('', views.home, name='database-home'),
    path('about/', views.about, name='database-about'),
    path('data/', views.data, name='database-data'),
    path('dashboard/', views.dash, name='database-dash'),
    path('project/<pk>/', ProjectView.as_view(), name='database-project'),
    path('export-csv/', views.export_csv, name='export_csv'),
]