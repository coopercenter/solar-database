from django.urls import path
from . import views
from .views import ProjectView

urlpatterns = [
    path('', views.home, name='database-home'),
    path('about/', views.about, name='database-about'),
    path('dashboard/', views.dashboard, name='database-dashboard'),
    path('data/', views.data, name='database-data'),
    path('project/<int:pk>/', ProjectView.as_view(), name='database-project')
]