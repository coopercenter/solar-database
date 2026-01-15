from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import SolarProjectData, DataDictionary, StorageProjectData
from django.views.generic import DetailView
from .plotly_dash import dashapp
from .plotly_dash_bat import dashappbat
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from django.urls import path, include
from io import BytesIO
from openpyxl import Workbook


def write_sheet(write_sheet, queryset, model):

    field_names = [
        f.name for f in model._meta.fields
    ]

    write_sheet.append(field_names)

    for obj in queryset.iterator():
        write_sheet.append([getattr(obj, field) for field in field_names])

    write_sheet.freeze_panes = "A2"

def export_xlsx(request):
    workbook = Workbook()

    write_sheet_solar = workbook.active
    write_sheet_solar.title = "Solar"

    excluded_fields = ['longitude', 'latitude', 'final_action_year']

    write_sheet(
        write_sheet_solar,
        SolarProjectData.objects.all(),
        SolarProjectData
    )

    write_sheet_storage = workbook.create_sheet(title="Storage")
    write_sheet(
        write_sheet_storage,
        StorageProjectData.objects.all(),
        StorageProjectData
    )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="projects.xlsx"'
    return response

def export_dictionary_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="va_solar_and_storage_data_dictionary.csv"'},
    )

    data = DataDictionary.objects.all()

    field_names = [field.name for field in DataDictionary._meta.fields]

    writer = csv.DictWriter(response, fieldnames=field_names)
    writer.writeheader()

    for obj in data:
        row = {field: getattr(obj, field) for field in field_names}
        writer.writerow(row)

    return response

def home(request):
    return render(request, 'database/home.html',)

def solar(request):
    map_data = list(SolarProjectData.objects.values('latitude', 'longitude', 'project_name', 
                                                'locality', 'project_mw', 
                                                'local_permit_status', 'data_id', 'alt_names'))

    data = SolarProjectData.objects.all()

    localities = SolarProjectData.objects.values_list('locality', flat=True).distinct().order_by('locality')
    localities = [loc for loc in localities if loc]    

    permit_status = SolarProjectData.objects.values_list('local_permit_status', flat=True).distinct().order_by('local_permit_status')
    permit_status = [status for status in permit_status if status]  # Filter out None/empty

    context = {
        'data': data,
        'map_data': map_data,
        'localities': localities,
        'permit_status': permit_status
    }
    return render(request, 'database/solar.html',context)

def about(request):
    return render(request, 'database/about.html')

def battery_storage(request):
    map_data = list(StorageProjectData.objects.values('latitude', 'longitude', 'project_name', 
                                                'locality', 'project_bess_mw', 
                                                'local_permit_status', 'data_id', 'alt_names'))

    data = StorageProjectData.objects.all()

    localities = StorageProjectData.objects.values_list('locality', flat=True).distinct().order_by('locality')
    localities = [loc for loc in localities if loc]    

    permit_status = StorageProjectData.objects.values_list('local_permit_status', flat=True).distinct().order_by('local_permit_status')
    permit_status = [status for status in permit_status if status]  # Filter out None/empty

    context = {
        'data': data,
        'map_data': map_data,
        'localities': localities,
        'permit_status': permit_status
    }

    return render(request, 'database/battery_storage.html', context)

def dictionary(request):
    
    datadictionary = DataDictionary.objects.all()
    context = {'datadictionary': datadictionary}

    return render(request, 'database/dictionary.html',context)

def donate(request):
    return render(request, 'database/donate.html')


class ProjectView(DetailView):
    model = SolarProjectData
    template_name = 'database/project.html'

class StorageProjectView(DetailView):
    model = StorageProjectData
    template_name = 'database/storage_project.html'
