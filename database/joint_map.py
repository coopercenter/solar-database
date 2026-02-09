from .models import SolarProjectData, CountyData, StorageProjectData
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.offline import plot
import requests
from django_plotly_dash import DjangoDash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import os

solarData = SolarProjectData.objects.values('data_id',
                                            'locality',
                                            'unit_of_government',
                                            'project_name',
                                            'project_mw',
                                            'local_permit_status',
                                            'latitude',
                                            'longitude',
                                            'energy_storage_onsite',
                                            'energy_storage_mw')
storageData = StorageProjectData.objects.values('data_id',
                                                'locality',
                                                'unit_of_government',
                                                'project_name',
                                                'project_bess_mw',
                                                'project_bess_capacity',
                                                'local_permit_status',
                                                'latitude',
                                                'longitude',
                                                'project_type')
solar_df = pd.DataFrame.from_records(solarData)
bess_df = pd.DataFrame.from_records(storageData)

#join the datasets on their common columns
joint_df = pd.merge(solar_df,bess_df,how='outer',on=['data_id',"locality",'unit_of_government','project_name','local_permit_status','latitude','longitude'])

#locate the Solar + Storage duplicate IDs
duplicate_ids = joint_df[joint_df['data_id'].duplicated()==True].data_id.to_list()

column_names = joint_df.columns.to_list()
for i in range(0,len(duplicate_ids)):
    #get the indices where a data_id value is duplicated because of mismatched names between Solar and BESS for Solar+Storage projects
    project_rows = joint_df[joint_df.data_id==duplicate_ids[i]].index
    #it will always be two project rows, project_row[0] and project_row[1]
    #pick ONE of the names, don't care which right now
    joint_df.loc[project_rows[0],'project_name'] = joint_df.loc[project_rows[1],'project_name']
    #go through the rest of the values and fill in the blanks to make duplicate rows
    for name in column_names:
        if pd.isna(joint_df.iloc[project_rows[0],][name]) == True and  pd.isna(joint_df.iloc[project_rows[1],][name]) == False:
            joint_df.loc[project_rows[0],name] = joint_df.loc[project_rows[1],name]
        if pd.isna(joint_df.iloc[project_rows[0],][name]) ==  False and  pd.isna(joint_df.iloc[project_rows[1],][name]) == True:
            joint_df.loc[project_rows[1],name] = joint_df.loc[project_rows[0],name]
#now that the rows have been made identical, drop the duplicated IDs
joint_df.drop_duplicates(inplace=True)

#filling in the missing values for project_type with 'Solar'
joint_df.project_type.replace(np.nan,'Solar',inplace=True)
#give a text description for where the bess MW is none
joint_df.project_bess_mw.replace(np.nan,'Not Applicable',inplace=True)
#give a text description for where the storage MW is none
joint_df.project_mw.replace(np.nan,'Not Applicable',inplace=True)

#set up the plotly Dash container
jointapp = DjangoDash(name='JointDash',add_bootstrap_links=True, external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.FLATLY,'/static/css/styles.css'])

jointapp.layout =  dbc.Container([
    #buid the state overview page
    html.Div([
        html.Br(),
        html.Br(),
        html.H2("Virginia Solar and Battery Energy Storage Status Map"),
        html.P("View the current status of Solar and Battery Energy Storage projects across Virginia"),
        html.Div(
            #dashboard
            [
            #developing reactive graph display based on Solar or Storage view selection     
           # html.H2("Select a Project Type to Graph",style={"margin-left":8}),  
            #html.Div(dbc.RadioItems(
            #    id='sourceButtons',
            #    className='btn-group',
            #    inputClassName='btn-check',
            #    labelClassName="btn btn--blue-d",
            #    options=[
            #],
            #value="solarMaps",
            #),style={'margin-left':4,}),
            html.Br(),
            html.Div(dbc.RadioItems(
                id='mapButtons',
            className='btn-group',
            inputClassName='btn-check',
            labelClassName="btn--dash",
            options=[
                {"label": "Approved", "value": 'Approved'},
                {"label": "Approved/Amended","value":"Approved/Amended"}, 
                {"label": "By-right", "value": 'By-right'},
                {"label": "Denied", "value": 'Denied'},
                {"label": "Withdrawn","value":'Withdrawn'},
                {"label": "Pending","value":'Pending'}
            ],
        value='Approved',
        ),style={'margin-left':4,}),
            #switchable maps
            html.Div(dcc.Graph(id='jointStatusMap',config={'responsive':False,
                                                     'displayModeBar':True}),
                     style={
                         'margin-left':9,
                         'width':1184,}), #close the map div
                             ]), #close the content div
                             ]
        )], #close the container contents list
                            fluid=True,
                            style={'display': 'flex',
                                   'background-color':'#F2F4F8'},
                            className='dashboard-container') #close the container div



#this will go in a callback function
@jointapp.callback(
        Output("jointStatusMap", "figure"),
        Input("mapButtons","value"))

def update_joint_amap(permit_status):
    jointMap = px.scatter_map(
            #mapDataClean[mapDataClean['final_action_year'] <= slide_year],
            joint_df[joint_df.local_permit_status==permit_status],
            color='project_type',
            custom_data=['project_name','project_type','locality','local_permit_status','project_mw','project_bess_mw'],
            color_discrete_sequence=['rgb(40, 67, 118)','rgb(98, 187, 70)','rgb(229, 114, 0)', 'rgb(253, 218, 36)'],
            category_orders={"project_type": ["Solar", "Solar + Storage", "Colocated with Solar", "Non-Solar BESS"]},
            labels={'locality':'Locality',
                    'local_permit_status':'Local Permit Status',
                    'project_type':"Project Type",
                    'project_mw':'Project Megawatts',
                    'project_bess_mw':"BESS Project Megawatts",
                    'project_name':'Project Name',
                    'locality': 'Locality'},
                    hover_name='project_name',
                    hover_data={
                                    'project_mw': True,
                                    'locality': True,
                                    'latitude':False,
                                    'longitude':False},
            lat='latitude',
            lon='longitude',
            zoom=6.57, 
            center = {"lat": 38.00692, "lon": -79.40695},
                    )
    jointMap.update_layout(
                    font=dict(color='#242e4c'),
                    legend=dict(font=dict(size=12,
                                        color='#242e4c'),
                                orientation='h',
                                yanchor='bottom',y=1),
                    legend2=dict(font=dict(size=12,
                                        color='#242e4c'),
                                title='Project Size'),
                    margin={"r":0,"t":10,"l":0,"b":0},
                    width=1155,
                    height=600,
                    map_style='carto-positron-nolabels',
                    paper_bgcolor='#F2F4F8',
                    xaxis=dict(showgrid=False,
                            zeroline=False,
                            visible=False),
                    yaxis=dict(showgrid=False,
                             zeroline=False,
                            visible=False),
                )
    jointMap.update_traces(marker=dict(size=10),
                                    hovertemplate="<b>%{customdata[0]}</b><br>Project Type : %{customdata[1]}<br>Locality: %{customdata[2]}<br>Local Permit Status: %{customdata[3]}<br>Solar Project Megawatts: %{customdata[4]}<br>BESS Project Megawatts: %{customdata[5]}<extra></extra>")
    jointMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)

    return jointMap

if __name__ == '__main__':
    jointapp.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))