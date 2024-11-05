from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import SolarProjectData
from django.views.generic import DetailView

import pandas as pd
import plotly.express as px
from plotly.offline import plot

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
    plotData = SolarProjectData.objects.values('latest_nameplate_capacity_per_local_action_mw_in_ac_field', 'local_permit_status')

    df = pd.DataFrame.from_records(plotData)

    df['local_permit_status'] = df['local_permit_status'].str.strip()

    mwPieData = df.groupby('local_permit_status').agg(
        {'latest_nameplate_capacity_per_local_action_mw_in_ac_field': 'sum'}
    ).reset_index()

    mwPieChart = px.pie(
        mwPieData,
        values = 'latest_nameplate_capacity_per_local_action_mw_in_ac_field', 
        names = 'local_permit_status',  
        color_discrete_sequence=[px.colors.qualitative.Safe[6], px.colors.qualitative.Safe[7], px.colors.qualitative.Safe[1], px.colors.qualitative.Safe[0], px.colors.qualitative.Safe[2], px.colors.qualitative.Safe[5]],
        title ='Total MW by Local Permit Status'
    )

    mwPieChart.update_layout(
        title = dict(
            text ='Total Megawatts by Local Permit Status',
            font = dict(size = 18, family ='Arial', color = 'black', weight= 600)
        ),
        legend = dict(
            font = dict(size = 12, family='Arial')
        )
    )

    mwPieChart.update_traces(
        textinfo = 'percent',
        textfont = dict(size = 14, family='Arial'),
        hovertemplate='<b>%{label}</b><br>Total: %{value} MW'  
    )

    mwPieChart_div = plot(mwPieChart, output_type='div')
    
    data = list(SolarProjectData.objects.values('latitude', 'longitude', 'project_name', 'locality', 'latest_nameplate_capacity_per_local_action_mw_in_ac_field', 'local_permit_status', 'data_id'))
    
    context = {
        'data': data,
        'mwPieChart_div': mwPieChart_div
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
