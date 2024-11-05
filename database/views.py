from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import SolarProjectData
from django.views.generic import DetailView

import pandas as pd
import numpy as np
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
    # plotData = SolarProjectData.objects.values('latest_nameplate_capacity_per_local_action_mw_in_ac_field', 
                                               # 'local_permit_status', 
                                               # 'best_available_project_acreage')

    # df = pd.DataFrame.from_records(plotData)

    # df['local_permit_status'] = df['local_permit_status'].str.strip()

     #mwPieData = df.groupby('local_permit_status').agg({'latest_nameplate_capacity_per_local_action_mw_in_ac_field': 'sum'}).reset_index()

    # mwPieChart = px.pie(
        # mwPieData,
        # values = 'latest_nameplate_capacity_per_local_action_mw_in_ac_field', 
        # names = 'local_permit_status',  
        # color_discrete_sequence=['rgb(37, 202, 211)', 'rgb(253, 218, 36)', 'rgb(229, 114, 0)', 'rgb(200, 203, 210)', 'rgb(35, 45, 75)','rgb(98, 187, 70)'],
        # category_orders={"local_permit_status": ["Approved", "Approved/Amended", "Denied", "Withdrawn", "By-right","Pending"]},
        # title ='Total MW by Local Permit Status',
    # )

    # mwPieChart.update_layout(
        # title = dict(
            # text ='Total Megawatts by Local Permit Status',
            # font = dict(size = 18, family ='Roboto', color = 'black', weight= 500)
        # ),
        # legend = dict(
            # font = dict(size = 12, family='Roboto')
        # )
    # )

    # mwPieChart.update_traces(
        # textinfo = 'percent + value',
        # textfont = dict(size = 14, family='Roboto'),
        # hovertemplate='<b>%{label}</b><br>Nameplate Capacity: %{value} MW'  
    # )

    # mwPieChart_div = plot(mwPieChart, output_type='div') 

    # acreageData = df.groupby('local_permit_status').agg({'best_available_project_acreage':'sum'}).reset_index()

    # acreageChart = px.bar(acreageData, x = 'local_permit_status', y='best_available_project_acreage',
                    # color_discrete_sequence = ['rgb(37, 202, 211)'],
                    # category_orders = {"Local Permit Status": ["Approved", "Approved/Amended", "Denied", "Withdrawn", "By-right", "Pending"]},
                    # labels = {
                    #'best_available_project_acreage': "Total Acreage",
                    # 'local_permit_status':''
                 # },
                 # title = "Project Acreage by Local Permit Status")
    
    # acreageChart.update_layout(
        # legend = dict(
            # font = dict(size = 12, family='Roboto')
        # ),
        # title = dict(
            # text ='Project Acreage by Local Permit Status',
            # font = dict(size = 18, family ='Roboto', color = 'black', weight= 500)
        # ),
    # )

    # acreageChart_div = plot(acreageChart, output_type='div')
    
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
