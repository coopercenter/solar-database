from django.shortcuts import render
from django.http import HttpResponse
from .models import SolarProjectData
from django.views.generic import DetailView


def home(request):
    data = list(SolarProjectData.objects.values('latitude', 'longitude', 'project_name', 'data_id',
                                                'sheep_grazing', 'apiaries', 'agrivoltaic_crop_cover'))

    context = {
        'data': data,
    }

    return render(request, 'database/home.html', context)

def about(request):
    return render(request, 'database/about.html')

def data(request):
    data = SolarProjectData.objects.all()
    project_name = request.GET.get('project_name')

    if project_name:
        data = data.filter(project_name__icontains=project_name)

    context = {
        'data': data,
    }

    return render(request, 'database/data.html', context)

class ProjectView(DetailView):
    model = SolarProjectData
    template_name = 'database/project.html'
