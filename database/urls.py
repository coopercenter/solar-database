from django.urls import path
from . import views
from .views import ProjectView
from django.urls import path, include
from .plotly_dash import dashapp

urlpatterns = [
    path('', views.home, name='database-home'),
    path('about/', views.about, name='database-about'),
    path('data/', views.data, name='database-data'),
    path('dashboard/', views.dash, name='dashboard-dash'),
    path('dictionary/', views.dictionary, name='database-dictionary'),
    path('project/<pk>/', ProjectView.as_view(), name='database-project'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('export-dictionary-csv/', views.export_dictionary_csv, name='export_dictionary_csv'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]