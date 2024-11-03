from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import SolarProjectData
from django.views.generic import DetailView

def export_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="solarprojects.csv"'},
    )

    data = SolarProjectData.objects.all()

    excluded_fields = {'longitude', 'latitude', 'year_of_final_action'}
    field_names = [field.name for field in SolarProjectData._meta.fields if field.name not in excluded_fields]

    writer = csv.DictWriter(response, fieldnames=field_names)
    writer.writeheader()

    for obj in data:
        row = {field: getattr(obj, field) for field in field_names}
        writer.writerow(row)

    return response

def dash(request):
    data = list(SolarProjectData.objects.values('latitude', 'longitude', 'project_name', 'locality', 'latest_nameplate_capacity_per_local_action_mw_in_ac_field', 'local_permit_status', 'data_id'))
    
    context = {
        'data': data,
    }

    return render(request, 'database/dash.html', context)

def about(request):
    return render(request, 'database/about.html')

def data(request):
    data = SolarProjectData.objects.all()

    context = {
        'data': data,
    }

    return render(request, 'database/data.html', context)

class ProjectView(DetailView):
    model = SolarProjectData
    template_name = 'database/project.html'
