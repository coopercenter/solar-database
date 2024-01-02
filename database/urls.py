from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='database-home'),
    path('about/', views.about, name='database-about'),
]