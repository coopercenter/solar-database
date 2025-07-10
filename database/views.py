from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import SolarProjectData, DataDictionary
from django.views.generic import DetailView
from .plotly_dash import dashapp
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from django.urls import path, include

def export_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="solarprojects.csv"'},
    )

    data = SolarProjectData.objects.all()

    excluded_fields = {'longitude', 'latitude', 'final_action_year', 'date_earliest_known_hearing'}
    field_names = [field.name for field in SolarProjectData._meta.fields if field.name not in excluded_fields]

    writer = csv.DictWriter(response, fieldnames=field_names)
    writer.writeheader()

    for obj in data:
        row = {field: getattr(obj, field) for field in field_names}
        writer.writerow(row)

    return response

def export_dictionary_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="vasolardatadictionary.csv"'},
    )

    data = DataDictionary.objects.all()

    field_names = [field.name for field in DataDictionary._meta.fields]

    writer = csv.DictWriter(response, fieldnames=field_names)
    writer.writeheader()

    for obj in data:
        row = {field: getattr(obj, field) for field in field_names}
        writer.writerow(row)

    return response

def dash(request):
    return render(request, 'database/dash.html',)

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

def dictionary(request):
    
    datadictionary = DataDictionary.objects.all()
    context = {'datadictionary': datadictionary}

    return render(request, 'database/dictionary.html',context)

def donate(request):
    return render(request, 'database/donate.html')


class ProjectView(DetailView):
    model = SolarProjectData
    template_name = 'database/project.html'
