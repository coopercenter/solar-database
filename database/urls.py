from django.urls import path
from . import views
from .views import ProjectView
from . import plotly_dash
from django.urls import path, include

urlpatterns = [
    path('', views.dash, name='database-home'),
    path('about/', views.about, name='database-about'),
    path('data/', views.data, name='database-data'),
    path('project/<pk>/', ProjectView.as_view(), name='database-project'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]