from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import SolarProjectData
from django.views.generic import DetailView

def export_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="allsolarprojects.csv"'},
    )

    data = SolarProjectData.objects.all()

    field_names = [field.name for field in SolarProjectData._meta.fields]
    writer = csv.DictWriter(response, fieldnames=field_names)
    writer.writeheader()

    for obj in data:
        writer.writerow({field.name: getattr(obj, field.name) for field in SolarProjectData._meta.fields})

    return response

def dash(request):
    data = list(SolarProjectData.objects.values('latitude', 'longitude', 'project_name', 'data_id'))
    
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
