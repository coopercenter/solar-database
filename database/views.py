from django.shortcuts import render
from django.http import HttpResponse
from .models import SolarProjectData
from django.views.generic import DetailView


def home(request):
    return render(request, 'database/home.html')

def about(request):
    return render(request, 'database/about.html')

def dashboard(request):
    return render(request, 'database/dashboard.html')

def data(request):
    context = {
        'data': SolarProjectData.objects.all(),
    }
    return render(request, 'database/data.html', context)

class ProjectView(DetailView):
    model = SolarProjectData
    template_name = 'database/project.html'
