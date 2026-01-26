from django.urls import path
from . import views
from .views import ProjectView
from django.urls import path, include
from .plotly_dash import dashapp
from .plotly_dash_bat import dashappbat
from .joint_map import jointapp

urlpatterns = [
    path('', views.home, name='database-home'),
    path('solar/', views.solar, name='database-solar'),
    path('about/', views.about, name='database-about'),
    path('battery_storage/', views.battery_storage, name='database-battery-storage'),
    path('dictionary/', views.dictionary, name='database-dictionary'),
    path('donate/', views.donate, name='database-donate'),
    path('project/<pk>/', ProjectView.as_view(), name='database-project'),
    path('export_xlsx/', views.export_xlsx, name='export_xlsx'),
    path('export-dictionary-csv/', views.export_dictionary_csv, name='export_dictionary_csv'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('storage-project/<pk>/', views.StorageProjectView.as_view(), name='database-storage-project'),
]