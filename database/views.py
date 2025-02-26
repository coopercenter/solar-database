from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import SolarProjectData
from django.views.generic import DetailView
from . import plotly_dash
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from plotly.offline import plot

def export_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="solarprojects.csv"'},
    )

    data = SolarProjectData.objects.all()

    excluded_fields = {'longitude', 'latitude', 'final_action_year'}
    field_names = [field.name for field in SolarProjectData._meta.fields if field.name not in excluded_fields]

    writer = csv.DictWriter(response, fieldnames=field_names)
    writer.writeheader()

    for obj in data:
        row = {field: getattr(obj, field) for field in field_names}
        writer.writerow(row)

    return response

def dash(request):
    app = DjangoDash(name='SolarDashTest',add_bootstrap_links=True, serve_locally=True, external_stylesheets=[dbc.themes.FLATLY])
    app.layout =  dbc.Container(html.H1('TESTING'))
    context = {
        'app':app
    }
    return render(request, 'database/dash.html',context)

def about(request):
    return render(request, 'database/about.html')

def data(request):
    map_data = list(SolarProjectData.objects.values('latitude', 'longitude', 'project_name', 
                                                'locality', 'project_mw', 
                                                'local_permit_status', 'data_id', 'alt_names'))
    data = SolarProjectData.objects.all()
    context = {
        'data': data,
        'map_data': map_data,
    }

    return render(request, 'database/data.html', context)

class ProjectView(DetailView):
    model = SolarProjectData
    template_name = 'database/project.html'
