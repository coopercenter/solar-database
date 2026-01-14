from .models import StorageProjectData, CountyData
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
#consider a visual update with https://www.dash-mantine-components.com/getting-started
#future graph analysis features https://www.datylon.com/blog/types-of-charts-graphs-examples-data-visualization

#get the dataset from the data we loaded in models.py
plotData = StorageProjectData.objects.values('data_id',
                                            'solar_storage',
                                            'project_type',
                                            'project_name',
                                            'project_bess_mw',
                                            'project_bess_capacity',
                                            'bess_duration_short_long',
                                            'local_permit_status',
                                            'public_bess_project_acres',
                                            'region',
                                            'final_action_year',
                                            'locality',
                                            'latitude',
                                            'longitude')
#define a base dataframe
df = pd.DataFrame.from_records(plotData)
#data munging to sort out some value inconsistencies and plotting needs
df.project_bess_capacity.replace("Not Found",0,inplace=True)
df.project_bess_capacity.replace(np.nan,0,inplace=True)
df.project_bess_capacity=df.project_bess_capacity.astype("float64")
#define the dataset for the pie charts
pieData = df[df["local_permit_status"]=="Approved"].groupby('project_type').agg({'project_bess_mw':'sum','project_bess_capacity':'sum','data_id':'count',}).reset_index()
#define the data used in the annual line charts, summing the relevant values by year and by status then calculating an annual rate of status action
annualData = pd.DataFrame(df[(df["local_permit_status"]!="Pending")&(df["project_type"]!="Solar + Storage")].groupby(['final_action_year','local_permit_status']).agg({'data_id':'count','project_bess_mw':'sum','project_bess_capacity':'sum'}).reset_index())
annualData = annualData.rename(columns={'data_id':'project_count'})
annualProjectTotal = df[(df["local_permit_status"]!="Pending")&(df["project_type"]!="Solar + Storage")].groupby('final_action_year').agg({'data_id':'count'}).reset_index()
annualProjectTotal = annualProjectTotal.rename(columns={'data_id':'annual_total'})
annualData = pd.merge(annualData,annualProjectTotal,on='final_action_year')
#annual status rate for all projects
annualData['annual_rate'] = round(annualData['project_count']/annualData['annual_total'],2)

#annual action rate data for approved/denied projects
actionRateData = df[df.local_permit_status.isin(["Approved","Denied"])].groupby(["final_action_year","local_permit_status"]).agg({"data_id":"count"}).reset_index().rename(columns={"data_id":"project_count"})
annualActionTotal = actionRateData.groupby("final_action_year").agg({"project_count":"sum"}).reset_index().rename(columns={"project_count":"annual_total"})
actionRateData=pd.merge(actionRateData,annualActionTotal,how="left",on="final_action_year")
actionRateData["action_rate"] = round(actionRateData['project_count']/actionRateData['annual_total'],2)

statusBar = df.groupby(["local_permit_status","project_type"]).agg({"data_id":"count","project_bess_mw":"sum","project_bess_capacity":"sum"}).reset_index()
#annual count for solar+storage projects
#annualSSTotal = annualData[annualData["project_type"]=="Solar + Storage"].groupby(['final_action_year']).agg({"data_id":"sum"}).reset_index()
#annualSSTotal.rename(columns={"data_id":"annual_solar_plus_storage"},inplace=True)
#annualData = pd.merge(annualData,annualSSTotal,on='final_action_year')

#annual count for solar colocated projects
#annualCSTotal = annualData[annualData["project_type"]=="Colocated with Solar"].groupby(['final_action_year']).agg({"data_id":"sum"}).reset_index()
#annualCSTotal.rename(columns={"data_id":"annual_solar_colocated"},inplace=True)
#annualData = pd.merge(annualData,annualCSTotal,on='final_action_year')

#annual count for bess no solar projects
#annualBESSTotal = annualData[annualData["project_type"]=="Non-Solar BESS"].groupby(['final_action_year']).agg({"data_id":"sum"}).reset_index()
#annualBESSTotal.rename(columns={"data_id":"annual_bess"},inplace=True)
#annualData = pd.merge(annualData,annualBESSTotal,on='final_action_year')



#annual status rate for solar+storage projects
#annualData['annual_rate_solar_plus_storage'] = round(annualData['project_count']/annualData['annual_solar_plus_storage'],2)

#annual status rate for colocated projects
#annualData['annual_rate_solar_colocated'] = round(annualData['project_count']/annualData['annual_solar_colocated'],2)

#annual rate for plain BESS
#annualData['annual_rate_bess'] = round(annualData['project_count']/annualData['annual_bess'],2)

#define the regional data, straightforward summary of relevant datapoints by region. More could be added
regionalData = pd.DataFrame(df.groupby(['region','local_permit_status']).agg({'project_bess_mw':'sum','data_id':'count','project_bess_capacity':"sum"}).reset_index())


#get the county fips crosswalk for mapping
countyData = CountyData.objects.values('locality',
                                        'fips',
                                        'locality_mapping')
countyDf = pd.DataFrame.from_records(countyData)

#get the county json 
counties = requests.get('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json').json()

mapData = pd.merge(df,countyDf,how='left',on='locality')
#set up the data for the permit status map with the time slider
mapDataClean = mapData[(mapData.local_permit_status != 'NA') & (mapData.final_action_year.isna()==False)]
mapDataClean['final_action_year']=mapDataClean.final_action_year.replace('PENDING',2026).astype("int")
years = mapDataClean['final_action_year'].unique()
years.sort()

#MW heatmap dataframe
heatMWYear = mapDataClean[(mapDataClean.local_permit_status.isin(['Approved','Denied'])) & (mapDataClean['final_action_year'].astype("int64") <= years[0])].groupby(['local_permit_status','fips','locality_mapping']).agg({'project_bess_mw':'sum','data_id':'count'}).reset_index()
heatMWYear['year']=years[0]

for year in years:
    heatMWYeari = mapDataClean[(mapDataClean.local_permit_status.isin(['Approved','Denied'])) & (mapDataClean['final_action_year'].astype("int64") <= year)].groupby(['local_permit_status','fips','locality_mapping']).agg({'project_bess_mw':'sum','data_id':'count'}).reset_index()
    heatMWYeari['year']=year
    heatMWYear = pd.concat([heatMWYear,heatMWYeari])

#status rate heatmap dataframe
statusRate = pd.DataFrame()
for year in years:
    all_fips = pd.DataFrame(mapDataClean[(mapDataClean['final_action_year'].astype("int64") <= year) &(mapDataClean['local_permit_status'] !='Pending')].groupby(['fips','locality_mapping']).agg({'project_bess_mw':'sum','data_id':'count'}).reset_index()).rename(columns={'project_bess_mw':'total_mw','data_id':'total_projects'})

    approved_fips = pd.DataFrame(mapDataClean[(mapDataClean.local_permit_status == 'Approved') & (mapDataClean['final_action_year']<= year)].groupby(['fips']).agg({'project_bess_mw':'sum','data_id':'count'}).reset_index()).rename(columns={'project_bess_mw':'approved_mw','data_id':'approved_projects'})

    denied_fips = pd.DataFrame(mapDataClean[(mapDataClean.local_permit_status == 'Denied') & (mapDataClean['final_action_year']<= year)].groupby(['fips']).agg({'project_bess_mw':'sum','data_id':'count'}).reset_index()).rename(columns={'project_bess_mw':'denied_mw','data_id':'denied_projects'})
    
    approved = pd.merge(all_fips,approved_fips,how='left',on='fips')
    approved_denied = pd.merge(approved,denied_fips,how='left',on='fips')
    approved_denied['year']=year
    statusRate = pd.concat([statusRate,approved_denied])

statusRate['approved_mw'] = statusRate['approved_mw'].replace(np.nan,0)
statusRate['approved_projects'] = statusRate['approved_projects'].replace(np.nan,0)
statusRate['approval_rate_mw']=round(statusRate['approved_mw']/statusRate['total_mw'],4)
statusRate['approval_rate_projects']=round(statusRate['approved_projects']/statusRate['total_projects'],4)

statusRate['denied_mw'] = statusRate['denied_mw'].replace(np.nan,0)
statusRate['denied_projects'] = statusRate['denied_projects'].replace(np.nan,0)
statusRate['denial_rate_mw']=round(statusRate['denied_mw']/statusRate['total_mw'],4)
statusRate['denial_rate_projects']=round(statusRate['denied_projects']/statusRate['total_projects'],4)



mwPieChart = px.pie(pieData,
                    title="<b>Approved Battery Storage Megawatts</b>",
                    values='project_bess_mw', 
                    names='project_type', 
                    color_discrete_sequence=['rgb(40, 67, 118)', 
                                             'rgb(253, 218, 36)', 
                                             'rgb(98, 187, 70)'],
                    category_orders={"local_permit_status": ["Non-Solar BESS", 
                                                             "Colocated with Solar", 
                                                             "Solar + Storage"]},
                    labels={'project_type':'Project Type',
                            'project_bess_mw':'Megawatts',
                            'data_id':'Project Count'},
                    hover_name='project_type',
                    hover_data={'project_type':False})
     
mwPieChart.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                         font_family='franklin-gothic-urw-cond, sans-serif',
                         title=dict(font=dict(size=22,color='#242e4c'), automargin=False, yref='paper'),
                         title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                         paper_bgcolor='#F2F4F8',
                         font_color='#242e4c',
                         autosize=False,
                         width=450,
                         height=660,
                         legend=dict(font=dict(size=10,
                                               color='#242e4c'),
                                      orientation='h',
                                      yanchor="bottom",
                                      y=.95,
                                      x=0,
                                      title=''))
     
#mwPieChart.update_traces(texttemplate="%{value:,.0f} MW (%{percent:.1%}) ",hovertemplate='<b>%{label}</b><br>Nameplate Megawatt Capacity: %{value:,.0f} MW')
mwPieChart.update_traces(texttemplate="%{value:,.0f} (%{percent:.1%}) ",hovertemplate='<b>%{label}</b><br>Nameplate Megawatt Capacity: %{value:,.0f} MW<br>Percent of Total Megawatts: %{percent:.1%}')
     
projectsPieChart= px.pie(pieData, 
                         values='data_id', 
                         names='project_type', 
                         title="<b>Approved Battery Storage Projects</b>",
                    color_discrete_sequence=['rgb(40, 67, 118)', 
                                             'rgb(253, 218, 36)', 
                                             'rgb(98, 187, 70)'],
                    category_orders={"local_permit_status": ["Non-Solar BESS", 
                                                             "Colocated with Solar", 
                                                             "Solar + Storage"]},
                         labels={'project_type':'Project Type',
                                 'data_id':'Total Projects'},
                         hover_name='project_type',
                         hover_data={'project_type':False})
     
projectsPieChart.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                               font_family='franklin-gothic-urw-cond, sans-serif',
                               title=dict(font=dict(size=22), automargin=False, yref='paper'),
                               title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                               paper_bgcolor='#F2F4F8',
                               font_color='#242e4c',
                               autosize=False,
                               width=450,
                               height=660,
                               legend=dict(font=dict(size=10,
                                                     color='#242e4c'),
                                           orientation='h',
                                           yanchor="bottom",
                                           y=.95,
                                           x=0,
                                           title=''))
     
projectsPieChart.update_traces(texttemplate="%{value} (%{percent:.1%}) ",hovertemplate='<b>%{label}</b><br>Projects: %{value:,.0f}<br> Percent of Total Projects: %{percent:.1%}')

    
mwhPieChart = px.pie(pieData, 
                      values='project_bess_capacity', 
                      names='project_type', 
                      title="<b>Approved Known Battery Storage MWh</b>",
                    color_discrete_sequence=['rgb(40, 67, 118)', 
                                             'rgb(253, 218, 36)', 
                                             'rgb(98, 187, 70)'],
                    category_orders={"local_permit_status": ["Non-Solar BESS", 
                                                             "Colocated with Solar", 
                                                             "Solar + Storage"]},
                      labels={'project_type':'Project Type',
                              'project_bess_capacity':'Known Megawatt Hours'},
                      hover_name='project_type',
                      hover_data={'project_type':False})
     
mwhPieChart.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                           font_family='franklin-gothic-urw-cond, sans-serif',
                           title=dict(font=dict(size=22), automargin=False, yref='paper'),
                           title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                           paper_bgcolor='#F2F4F8',
                           font_color='#242e4c',
                           autosize=False,
                           width=450,
                           height=660,
                           legend=dict(font=dict(size=10,
                                                 color='#242e4c'),
                                       orientation='h',
                                       yanchor="bottom",
                                       y=.95,
                                       x=0,
                                       title=''))
     
mwhPieChart.update_traces(texttemplate="%{value:,.3s} (%{percent:.1%}) ",hovertemplate='<b>%{label}</b><br>Known Project MWh: %{value:,.0f}<br>Percent of Known Total MWh: %{percent:.1%}')

actionAnnualLine = px.line(actionRateData,  
                         x="final_action_year", 
                         y='action_rate',
                         color='local_permit_status',
                         title="<b>Annual Battery Storage Action Rate</b>",
                         custom_data = ['local_permit_status','project_count','annual_total'],
                         height=660,
                         width=600,
                         markers=True,
                         color_discrete_sequence=['rgb(40, 67, 118)', 
                                                  'rgb(253, 218, 36)', 
                                                  'rgb(229, 114, 0)',
                                                  'rgb(200, 203, 210)',
                                                  'rgb(37, 202, 211)',
                                                  'rgb(98, 187, 70)'],
                         category_orders={"local_permit_status": ["Approved", 
                                                                  "Approved/Amended", 
                                                                  "Denied", 
                                                                  "Withdrawn", 
                                                                  "By-right", 
                                                                  "Pending"]},
                         labels={"final_action_year":'Year',
                                 'local_permit_status':'Action Taken',
                                 'annual_rate':'Action Rate',
                                 'annual_total':'Total Projects for Year',
                                 'project_count':'Action Projects'})

actionAnnualLine.update_traces(line=dict(width=2),
                             marker=dict(size=10),
                             hovertemplate='<b>%{customdata[0]}</b><br>Year: %{x}<br>Percent %{customdata[0]}: %{y}<br>%{customdata[0]} Projects: %{customdata[1]}<br>Total Projects: %{customdata[2]}<br><extra></extra>')

actionAnnualLine.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                             font_family='franklin-gothic-urw-cond, sans-serif',
                             title=dict(font=dict(size=22), automargin=False, yref='paper'),
                             paper_bgcolor='#F2F4F8',
                             plot_bgcolor='#F2F4F8',
                             legend=dict(font=dict(size=10,
                                                   color='#242e4c'),
                                         orientation='h',
                                         yanchor="bottom",
                                         y=1,
                                         x=0,
                                         title=''),
                             font=dict(size=10,
                                       color='#242e4c'),
                             title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                             yaxis=dict(title="Percent of Projects",tickformat='.0%'),
                             xaxis=dict(type='category',
                                        tickmode='array',
                                        tickvals=[2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024,2025],
                                        categoryorder='category ascending',
                                        title=''))

rateAnnualLine = px.line(annualData,  
                         x="final_action_year", 
                         y='annual_rate',
                         color='local_permit_status',
                         title="<b>Annual Battery Storage Local Status Rate</b>",
                         custom_data = ['local_permit_status','project_count','annual_total'],
                         height=660,
                         width=600,
                         markers=True,
                         color_discrete_sequence=['rgb(40, 67, 118)', 
                                                  'rgb(253, 218, 36)', 
                                                  'rgb(229, 114, 0)',
                                                  'rgb(200, 203, 210)',
                                                  'rgb(37, 202, 211)',
                                                  'rgb(98, 187, 70)'],
                         category_orders={"local_permit_status": ["Approved", 
                                                                  "Approved/Amended", 
                                                                  "Denied", 
                                                                  "Withdrawn", 
                                                                  "By-right", 
                                                                  "Pending"]},
                         labels={"final_action_year":'Year',
                                 'local_permit_status':'Local Permit Status',
                                 'annual_rate':'Status Rate',
                                 'annual_total':'Total Projects for Year',
                                 'project_count':'Status Projects'})

rateAnnualLine.update_traces(line=dict(width=2),
                             marker=dict(size=10),
                             hovertemplate='<b>%{customdata[0]}</b><br>Year: %{x}<br>Percent %{customdata[0]}: %{y}<br>%{customdata[0]} Projects: %{customdata[1]}<br>Total Projects: %{customdata[2]}<br><extra></extra>')

rateAnnualLine.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                             font_family='franklin-gothic-urw-cond, sans-serif',
                             title=dict(font=dict(size=22), automargin=False, yref='paper'),
                             paper_bgcolor='#F2F4F8',
                             plot_bgcolor='#F2F4F8',
                             legend=dict(font=dict(size=10,
                                                   color='#242e4c'),
                                         orientation='h',
                                         yanchor="bottom",
                                         y=1,
                                         x=0,
                                         title=''),
                             font=dict(size=10,
                                       color='#242e4c'),
                             title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                             yaxis=dict(title="Percent of Projects",tickformat='.0%'),
                             xaxis=dict(type='category',
                                        tickmode='array',
                                        tickvals=[2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024,2025],
                                        categoryorder='category ascending',
                                        title=''))


mwAnnualLine = px.line(annualData,
                       x="final_action_year", 
                       y="project_bess_mw",
                       color='local_permit_status',
                       title="<b>Annual Battery Storage Megawatts by Local Permit Status</b>",
                       custom_data=['local_permit_status','project_count'],
                       height=660,
                       width=600,
                       markers=True,
                       color_discrete_sequence=['rgb(40, 67, 118)', 
                                                'rgb(253, 218, 36)', 
                                                'rgb(229, 114, 0)', 
                                                'rgb(200, 203, 210)',
                                                'rgb(37, 202, 211)',
                                                'rgb(98, 187, 70)'],
                       category_orders={"local_permit_status": ["Approved", 
                                                                "Approved/Amended", 
                                                                "Denied", 
                                                                "Withdrawn", 
                                                                "By-right", 
                                                                "Pending"]},
                       labels={'final_action_year':'Year',
                                'local_permit_status':'Local Permit Status',
                                'project_bess_mw':'Megawatts'})
     
mwAnnualLine.update_traces(line=dict(width=2),
                           marker=dict(size=10),
                           hovertemplate='<b>%{customdata[0]}</b><br>Year: %{x}<br>Megawatts: %{y}<br>Projects: %{customdata[1]}<br><extra></extra>')

mwAnnualLine.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                           font_family='franklin-gothic-urw-cond, sans-serif',
                           title=dict(font=dict(size=22), automargin=False, yref='paper'),
                           title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                           paper_bgcolor='#F2F4F8',
                           plot_bgcolor='#F2F4F8',
                           font=dict(size=10,
                                     color='#242e4c'),
                           legend=dict(font=dict(size=10,
                                                 color='#242e4c'),
                                       orientation='h',
                                       yanchor="bottom",
                                       y=1,
                                       x=0,
                                       title=''),
                           xaxis=dict(title='',
                                      type='category',
                                      categoryorder='category ascending',
                                      tickmode='array',
                                      tickvals=[2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]),
                           yaxis=dict(tickformat=",.0f",
                                      title="Megawatts"))
mwhAnnualLine = px.line(annualData,
                       x="final_action_year", 
                       y="project_bess_capacity",
                       color='local_permit_status',
                       title="<b>Annual Known Battery Storage MWh by Local Permit Status</b>",
                       custom_data=['local_permit_status','project_count'],
                       height=660,
                       width=600,
                       markers=True,
                       color_discrete_sequence=['rgb(40, 67, 118)', 
                                                'rgb(253, 218, 36)', 
                                                'rgb(229, 114, 0)', 
                                                'rgb(200, 203, 210)',
                                                'rgb(37, 202, 211)',
                                                'rgb(98, 187, 70)'],
                       category_orders={"local_permit_status": ["Approved", 
                                                                "Approved/Amended", 
                                                                "Denied", 
                                                                "Withdrawn", 
                                                                "By-right", 
                                                                "Pending"]},
                       labels={'final_action_year':'Year',
                                'local_permit_status':'Local Permit Status',
                                'project_bess_capacity':'Known Megawatt Hours'})
     
mwhAnnualLine.update_traces(line=dict(width=2),
                           marker=dict(size=10),
                           hovertemplate='<b>%{customdata[0]}</b><br>Year: %{x}<br>Known Megawatt Hours: %{y}<br>Projects: %{customdata[1]}<br><extra></extra>')

mwhAnnualLine.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                           font_family='franklin-gothic-urw-cond, sans-serif',
                           title=dict(font=dict(size=22), automargin=False, yref='paper'),
                           title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                           paper_bgcolor='#F2F4F8',
                           plot_bgcolor='#F2F4F8',
                           font=dict(size=10,
                                     color='#242e4c'),
                           legend=dict(font=dict(size=10,
                                                 color='#242e4c'),
                                       orientation='h',
                                       yanchor="bottom",
                                       y=1,
                                       x=0,
                                       title=''),
                           xaxis=dict(title='',
                                      type='category',
                                      categoryorder='category ascending',
                                      tickmode='array',
                                      tickvals=[2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]),
                           yaxis=dict(tickformat=",.0f",
                                      title="Megawatts"))

projectsAnnualLine = px.line(annualData[(annualData['final_action_year'] != 'PENDING') & (annualData['local_permit_status'] != 'NA')],
                             x="final_action_year", 
                             y="project_count",
                             color='local_permit_status',
                             title="<b>Annual Battery Storage Projects by Local Permit Status</b>",
                             custom_data=['local_permit_status','project_bess_mw'],
                             height=660,
                             width=600,
                             markers=True,
                             color_discrete_sequence=['rgb(40, 67, 118)', 
                                                      'rgb(253, 218, 36)', 
                                                      'rgb(229, 114, 0)', 
                                                      'rgb(200, 203, 210)',
                                                      'rgb(37, 202, 211)',
                                                      'rgb(98, 187, 70)'],
                             category_orders={"local_permit_status": ["Approved", 
                                                                      "Approved/Amended", 
                                                                      "Denied", 
                                                                      "Withdrawn", 
                                                                      "By-right", 
                                                                      "Pending"]},
                             labels={'final_action_year':'Year',
                                     'local_permit_status':'Local Permit Status',
                                     'project_count':'Project Count'})
     
projectsAnnualLine.update_traces(line=dict(width=2),
                                 marker=dict(size=10),
                                 hovertemplate="<b>%{customdata[0]}</b><br>Year: %{x}<br>Projects: %{y}<br>Megawatts: %{customdata[1]:,.0f}<br><extra></extra>")

projectsAnnualLine.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                                 font_family='franklin-gothic-urw-cond, sans-serif',
                                 title=dict(font=dict(size=22), automargin=False, yref='paper'),
                                 title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                                 paper_bgcolor='#F2F4F8',
                                 plot_bgcolor='#F2F4F8',
                                 font=dict(size=10,color='#242e4c'),
                                 legend=dict(font=dict(size=10,
                                                       color='#242e4c'),
                                             orientation='h',
                                             yanchor="bottom",
                                             y=1,
                                             x=0,
                                             title=''),
                                 xaxis=dict(title='',
                                            tickmode='array',
                                            tickvals=[2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
                                            type='category',
                                            categoryorder='category ascending'),
                                 yaxis=dict(tickformat=",.0f",
                                            title="Projects"))


mwRegionalBar = px.bar(regionalData, 
                       x="region", 
                       y='project_bess_mw', 
                       color='local_permit_status',
                       title="<b>Regional Megawatts by Local Permit Status</br>",
                       custom_data=['local_permit_status','project_bess_capacity','data_id'],
                       height=640,
                       width=600,
                       color_discrete_sequence=['rgb(40, 67, 118)', 
                                                'rgb(253, 218, 36)', 
                                                'rgb(229, 114, 0)', 
                                                'rgb(200, 203, 210)',
                                                'rgb(37, 202, 211)',
                                                'rgb(98, 187, 70)'],
                      category_orders={"local_permit_status": ["Approved", 
                                                               "Approved/Amended", 
                                                               "Denied", 
                                                               "Withdrawn", 
                                                               "By-right", 
                                                               "Pending"]},
                      labels={"region":'Region',
                              'project_bess_mw':'Megawatts',
                              'project_bess_capacity':'Known Megawatt Hours',
                              'data_id':'Project Count',
                              'local_permit_status':'Local Permit Status'},
                      barmode='stack')
mwRegionalBar.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Region: %{x}<br>%{customdata[0]} Megawatts: %{y}<br>%{customdata[0]} Projects: %{customdata[2]}<br>%{customdata[0]} Known Megawatt Hours: %{customdata[1]:,.0f}<br><extra></extra>")

mwRegionalBar.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                            paper_bgcolor='#F2F4F8',
                            plot_bgcolor='#F2F4F8',
                            legend=dict(font=dict(size=10,
                                                  color='#242e4c'),
                                         orientation='h',
                                         yanchor="bottom",
                                         y=.95,
                                         x=0,
                                         title=''),
                            font=dict(size=10,color='#242e4c'),
                            font_family='franklin-gothic-urw-cond, sans-serif',
                            title=dict(font=dict(size=22), automargin=False, yref='paper'),
                            title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                            xaxis=dict(categoryorder='total descending',
                                       tickangle=45,
                                       tickmode='array',
                                       tickvals=['Southern','Central','Hampton Roads','Valley','Northern','Eastern','West Central','Southwest'],title=''),
                            yaxis=dict(tickformat=",.0f",
                                       title="Megawatts"))


mwStatusBar = px.bar(statusBar, 
                       x="project_bess_mw", 
                       y='local_permit_status', 
                       color='project_type',
                       title="<b>Megawatts, All Projects</br>",
                       custom_data=['local_permit_status','project_bess_capacity','data_id'],
                       height=640,
                       width=600,
                        color_discrete_sequence=['rgb(40, 67, 118)', 
                                             'rgb(253, 218, 36)', 
                                             'rgb(98, 187, 70)'],
                        category_orders={"local_permit_status": ["Non-Solar BESS", 
                                                             "Colocated with Solar", 
                                                             "Solar + Storage"]},
                      labels={"project_type":'Project Type',
                              'project_bess_mw':'Megawatts',
                              'project_bess_capacity':'Known Megawatt Hours',
                              'data_id':'Project Count',
                              'local_permit_status':'Local Permit Status'},
                      barmode='stack')
mwStatusBar.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Region: %{x}<br>%{customdata[0]} Megawatts: %{y}<br>%{customdata[0]} Projects: %{customdata[2]}<br>%{customdata[0]} Known Megawatt Hours: %{customdata[1]:,.0f}<br><extra></extra>")

mwStatusBar.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                            paper_bgcolor='#F2F4F8',
                            plot_bgcolor='#F2F4F8',
                            legend=dict(font=dict(size=10,
                                                  color='#242e4c'),
                                         orientation='h',
                                         yanchor="bottom",
                                         y=.95,
                                         x=0,
                                         title=''),
                            font=dict(size=10,color='#242e4c'),
                            font_family='franklin-gothic-urw-cond, sans-serif',
                            title=dict(font=dict(size=22), automargin=False, yref='paper'),
                            title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                            xaxis=dict(
                                       tickformat=",.0f",
                                       title='Megawatts'),
                            yaxis=dict(
                                       
                                       tickvals=['Approved','Approved/Amended','By-right','Denied','Withdrawn','Pending'],
                                       title="Local Permit Status"))

mwhStatusBar = px.bar(statusBar, 
                       x="project_bess_capacity", 
                       y='local_permit_status', 
                       color='project_type',
                       title="<b>Known Megawatt Hours, All Projects</br>",
                       custom_data=['local_permit_status','project_bess_mw','data_id'],
                       height=640,
                       width=600,
                    color_discrete_sequence=['rgb(40, 67, 118)', 
                                             'rgb(253, 218, 36)', 
                                             'rgb(98, 187, 70)'],
                    category_orders={"local_permit_status": ["Non-Solar BESS", 
                                                             "Colocated with Solar", 
                                                             "Solar + Storage"]},
                      labels={"project_type":'Project Type',
                              'project_bess_mw':'Megawatt Hours',
                              'project_bess_capacity':'Known Megawatt Hours',
                              'data_id':'Project Count',
                              'local_permit_status':'Local Permit Status'},
                      barmode='stack')
mwhStatusBar.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Region: %{x}<br>%{customdata[0]} Megawatts: %{y}<br>%{customdata[0]} Projects: %{customdata[2]}<br>%{customdata[0]} Known Megawatt Hours: %{customdata[1]:,.0f}<br><extra></extra>")

mwhStatusBar.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                            paper_bgcolor='#F2F4F8',
                            plot_bgcolor='#F2F4F8',
                            legend=dict(font=dict(size=10,
                                                  color='#242e4c'),
                                         orientation='h',
                                         yanchor="bottom",
                                         y=.95,
                                         x=0,
                                         title=''),
                            font=dict(size=10,color='#242e4c'),
                            font_family='franklin-gothic-urw-cond, sans-serif',
                            title=dict(font=dict(size=22), automargin=False, yref='paper'),
                            title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                            xaxis=dict(tickformat=",.0f",
                                       title='Megawatt Hours'),
                            yaxis=dict(
                                       
                                       tickvals=['Approved','Approved/Amended','By-right','Denied','Withdrawn','Pending'],
                                       title="Local Permit Status"))     

dashappbat = DjangoDash(name='BatteryDash',add_bootstrap_links=True, external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.FLATLY,'/static/css/styles.css'])

dashappbat.layout =  dbc.Container([
    #buid the state overview page
    html.Div([
        html.Br(),
        html.Br(),
        html.H1("Virginia Battery Storage Dashboard"),
        html.P("Visualizations reflect all projects in the database as of December 31, 2025. Explore different data highlights with the buttons, and download a graph with the camera icon in the upper right corner of each graph. Hovertext labels on all maps and graphs provide supplemental information."),
        html.Div(
            #dashboard
            [
            #developing reactive graph display based on Solar or Battery view selection     
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
                {"label": "Local Permit Status", "value": 'statusPermitMap'},
                {"label": "Approved Megawatts", "value": 'approvedMWMap'},
                {"label": "Denied Megawatts", "value": 'deniedMWMap'},
                {"label": "Project Approval Rate","value":'approvedRateMap'},
                {"label": "Project Denial Rate","value":'deniedRateMap'}
            ],
        value='statusPermitMap',
        ),style={'margin-left':4,}),
            #switchable maps
            html.Div(dcc.Graph(id='stateMap',config={'responsive':False,
                                                     'displayModeBar':True}),
                     style={
                         'margin-left':9,
                         'width':1184,
                     }),
            html.Div([
            html.Label("Select year to map project development over time", htmlFor="years"),
            dcc.Slider(mapDataClean['final_action_year'].min(),
                       mapDataClean['final_action_year'].max(),
                       step=1, 
                       value=mapDataClean['final_action_year'].max(),
                       marks={str(year): str(year) for year in mapDataClean['final_action_year'].unique()},
                      id='years'
            )],
            style={'width':1155,
                   'margin-left':8,})
                             ]),
        #summary graphs
        html.Div(
        [dbc.Row([
            #pie chart block
            html.Div([
            #pie chart universal title
            #html.H3('Local Permit Status Summaries'),
            #pie chart buttons
            dbc.RadioItems(
                id='graphOneButtons',
            className='btn-group',
            inputClassName='btn-check',
            labelClassName="btn--dash",
            options=[
                {"label": "Projects", "value": 'projectsPie'},
                {"label": "Megawatts", "value": 'mwPie'},
                {"label": "Known Megawatt Hours", "value": 'mwhPie'}
            ],
        value='projectsPie'
        ),
            #pie chart block
            html.Div(dcc.Graph(id='graphOne',config={'responsive':False,
                                                     'displayModeBar':True}))]), 
            #size category block
            html.Div([
            #size categories universal title
            #html.H3('Size Category Summaries'),
            #size category buttons
            dbc.RadioItems(
                id='graphThreeButtons',
                className='btn-group',
                inputClassName='btn-check',
                labelClassName="btn--dash",
                options=[
                {"label": "Megawatts", "value": 'mwStatusBar'}, 
                {"label": "Known Megawatt Hours", "value": 'mwhStatusBar'}
                
            ],
        value='mwStatusBar'
            ),
            #size category bar chart
            html.Div(dcc.Graph(id='graphThree',config={'responsive':False,
                                                    'displayModeBar':True}),style={'height':640})])
                ]),
        dbc.Row([
            #annual line chart block
            html.Div([
            #annual chart universal title
            #html.H3('Annual Data by Local Permit Status'),
            #annual chart buttons
            dbc.RadioItems(
                id='graphTwoButtons',
                className='btn-group',
                inputClassName='btn-check',
                labelClassName="btn--dash",
                        options=[
                {"label": "Local Status Rate", "value": 'statusLine'},
                {"label": "Action Rate", "value": 'rateLine'},
                {"label": "Megawatts", "value": 'mwLine'}, 
                {"label": "Projects", "value": 'projectsLine'}
            ],
        value='statusLine'
            ),
            #annual line chart
            html.Div(dcc.Graph(id='graphTwo',config={'responsive':False,
                                                       'displayModeBar':True}),
                    style={'width':600,})]),
            #regional bar block
            html.Div([
                dbc.RadioItems(
                id='graphFourButtons',
                className='btn-group',
                inputClassName='btn-check',
                labelClassName="btn--dash",
                options=[
                {"label": "Regional Megawatts", "value": 'mwRegionalBar'},  
            ],
        value='mwRegionalBar'
            ),
                #regional title
                #html.H3('Regional Megawatts by Local Permit Status'), 
                #regional graph
                dcc.Graph(id='graphFour',config={'responsive':False,
                                                       'displayModeBar':True})],
                style={'width':600,
                       'height':715,
                       'margin-top':35})
            ],
            style={'margin-right':0,
                   'margin-left':60,})
            ],
        style={
            #style the container that holds the graphs
            'margin-top': 35,
            'margin-right': 0,
            'margin-left':10,
            'margin-bottom': 35,
            'display': 'flex'
        })])],
                            fluid=True,
                            style={'display': 'flex'},
                            className='dashboard-container')

#Define a callback to plot the map with a time slider
#@dashapp.callback(
#        Output("mapButtons","options"),
#        Output("mapButtons","value"),
#        Input("sourceButtons","value")
#)

#def populate_top_buttons(source_type):
#    if source_type=="solarMaps":
#        options=[
#                {"label": "Local Permit Status", "value": 'statusPermitMap'},
#                {"label": "Project Size", "value": 'sizeMap'}, 
#                {"label": "Approved Megawatts", "value": 'approvedMWMap'},
#                {"label": "Denied Megawatts", "value": 'deniedMWMap'},
#                {"label": "Project Approval Rate","value":'approvedRateMap'},
#                {"label": "Project Denial Rate","value":'deniedRateMap'}
#            ]
#        value='statusPermitMap'
#        return options, value
#    if source_type == "solarGraphs":
#        options=[]
#        value='rateLine'
#        return options,value

#@dashapp.callback(
#        Output('graphOneButtons',"options"),
#        Output('graphOneButtons',"value"),
#        Input("sourceButtons","value")
#)
#def populate_graph1_buttons(source_type):
#    if source_type == "solarGraphs":
##        options=[
 #               {"label": "Megawatts", "value": 'mwPie'}, 
 #               {"label": "Projects", "value": 'projectsPie'},
 #               {"label": "Best Available Acres", "value": 'acresPie'}
 #           ]
 #       value='mwPie'
 #       return options, value
 #   if source_type=="solarMaps":
 #       options=[
 #               {"label": "Megawatts", "value": 'mwPie'}, 
 #               {"label": "Projects", "value": 'projectsPie'},
 #               {"label": "Best Available Acres", "value": 'acresPie'}
 #           ]
 #       value='mwPie'
 #       return options,value

#@dashapp.callback(
#        Output('graphTwoButtons',"options"),
#        Output('graphTwoButtons',"value"),
#        Input("sourceButtons","value")
#)
#def populate_graph2_buttons(source_type):
#    if source_type == "solarGraphs":
#        options=[
#                {"label": "Action Rate", "value": 'rateLine'},
#                {"label": "Megawatts", "value": 'mwLine'}, 
#                {"label": "Projects", "value": 'projectsLine'}
#            ]
#        value='rateLine'
#        return options, value
#    if source_type=="solarMaps":
#        options=[]
#        value='rateLine'
#        return options,value

#@dashapp.callback(
#        Output('graphThreeButtons',"options"),
#        Output('graphThreeButtons',"value"),
#        Input("sourceButtons","value")
#)
#def populate_graph3_buttons(source_type):
#    if source_type == "solarGraphs":
#        options=[
#                {"label": "Megawatts", "value": 'sizeMWBar'}, 
#                {"label": "Projects", "value": 'sizeProjectsBar'},
#                {"label": "Action Rate", "value": 'sizePercentBar'}
#                
#            ]
#        value='sizeMWBar'
#        return options, value
#    elif source_type=="solarMaps":
#        options=[
#                {"label": "Megawatts", "value": 'sizeMWBar'}, 
#                {"label": "Projects", "value": 'sizeProjectsBar'},
#                {"label": "Action Rate", "value": 'sizePercentBar'}  
#            ]
#        value='sizeMWBar'
#        return options,value
    
#@dashapp.callback(
##        Output('graphFourButtons',"options"),
 #       Output('graphFourButtons',"value"),
 #       Input("sourceButtons","value")
#)

#def populate_graph4_buttons(source_type):
#    if source_type == "solarGraphs":
#        options=[
#                {"label": "Regional Megawatts", "value": 'mwRegionalBar'},  
#            ]
#        value='mwRegionalBar'
#        return options, value
#    if source_type=="solarMaps":
#        options=[
#                {"label": "Regional Megawatts", "value": 'mwRegionalBar'},  
#            ]
#        value='mwRegionalBar'
#        return options,value

@dashappbat.callback(
        Output("stateMap", "figure"),
        Input("mapButtons","value"),
        Input("years", "value"))

def update_map(map_type,slide_year):
    if map_type=='statusPermitMap':
        statusMap = px.scatter_map(
            mapDataClean[mapDataClean['final_action_year'] <= slide_year],
            color='local_permit_status',
            custom_data=['project_name','locality','local_permit_status','final_action_year','project_bess_mw'],
            color_discrete_sequence=['rgb(40, 67, 118)', 'rgb(253, 218, 36)', 'rgb(229, 114, 0)', 'rgb(200, 203, 210)','rgb(37, 202, 211)','rgb(98, 187, 70)'],
            category_orders={"local_permit_status": ["Approved", "Approved/Amended", "Denied", "Withdrawn", "By-right", "Pending"]},
            labels={'locality':'Locality',
                    'local_permit_status':'Local Permit Status',
                    'project_bess_mw':'Project Megawatts',
                    'project_name':'Project Name',
                    'project_phase':'Phase Name',
                    'phase_mw':'Phase Megawatts',
                    'final_action_year':'Year',
                    'locality': 'Locality'},
                    hover_name='project_name',
                    hover_data={'final_action_year':True,
                                    'project_bess_mw': True,
                                    'locality': True,
                                    'latitude':False,
                                    'longitude':False},
            lat='latitude',
            lon='longitude',
            zoom=6.57, 
            center = {"lat": 38.00692, "lon": -79.40695},
                    )
        statusMap.update_layout(
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
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False,
                            zeroline=False,
                            visible=False),
                    yaxis=dict(showgrid=False,
                             zeroline=False,
                            visible=False)
                )
        statusMap.update_traces(marker=dict(size=10),
                                    hovertemplate="<b>%{customdata[0]}</b><br>Locality: %{customdata[1]}<br>Local Permit Status: %{customdata[2]}<br>Project Megawatts: %{customdata[5]:,.0f}<br>Year: %{customdata[4]}<br>Best Available Project Acreage: %{customdata[6]:,.0f}<br><extra></extra>")
        statusMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)


        return statusMap
    
    elif map_type=='approvedMWMap':
        approvedMWMap = px.choropleth_map(heatMWYear[(heatMWYear['local_permit_status']=='Approved') & (heatMWYear['year']==slide_year)],
                                         geojson=counties, 
                                         locations='fips', 
                                         color='project_bess_mw',
                                         custom_data=['locality_mapping','project_bess_mw','data_id'],
                                         color_continuous_scale=['#F2F4F8','rgb(40, 67, 118)'],
                                         range_color=(0, 500),
                                         zoom=6.37, center = {"lat": 38.00692, "lon": -79.40695},
                                         opacity=1,
                                         labels={'project_bess_mw':'Approved<br>Megawatts',
                                                 'data_id':'Number of Projects'})
        approvedMWMap.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Approved Megawatts: %{customdata[1]:,.0f}<br>Approved Projects: %{customdata[2]:,.0f}<br><extra></extra>")
        approvedMWMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                        width=1155,
                        height=600,
                        map_style='carto-positron-nolabels',
                        paper_bgcolor='rgba(0,0,0,0)',
                        coloraxis_colorbar=dict(tickfont=dict(size=10,color='#242e4c'),orientation='h')
                  )
        approvedMWMap.update_coloraxes(colorbar_labelalias={500:'500 and above'})
        approvedMWMap.update_geos(
                fitbounds='locations'
            )
        approvedMWMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)
        return approvedMWMap
    
    elif map_type=='deniedMWMap':
        deniedMWMap = px.choropleth_map(heatMWYear[(heatMWYear['local_permit_status']=='Denied') & (heatMWYear['year']==slide_year)], 
                                        geojson=counties, 
                                        locations='fips', 
                                        color='project_bess_mw',
                                        custom_data=['locality_mapping','project_bess_mw','data_id'],
                                        color_continuous_scale=['#F2F4F8','rgb(229, 114, 0)'],
                                        range_color=(0, 500),
                                        zoom=6.37, center = {"lat": 38.00692, "lon": -79.40695},
                                        opacity=1,
                                        labels={'project_bess_mw':'Denied<br>Megawatts',
                                                'data_id':'Number of Projects'})
        deniedMWMap.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Denied Megawatts: %{customdata[1]:,.0f}<br>Denied Projects: %{customdata[2]:,.0f}<br><extra></extra>")
        deniedMWMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                                  width=1155,
                                  height=600,
                                  map_style='carto-positron-nolabels',
                                  paper_bgcolor='rgba(0,0,0,0)',
                                  coloraxis_colorbar=dict(tickfont=dict(size=10,color='#242e4c'),orientation='h'))
        deniedMWMap.update_coloraxes(colorbar_labelalias={500:'500 and above'})
        deniedMWMap.update_geos(fitbounds='locations')
        deniedMWMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)
        return deniedMWMap
    elif map_type=='approvedRateMap':
        approvedRateMap = px.choropleth_map(statusRate[statusRate['year']==slide_year], 
                                            geojson=counties, 
                                            locations='fips', 
                                            color='approval_rate_projects',
                                            color_continuous_scale=['#F2F4F8','rgb(40, 67, 118)'],
                                            custom_data=['locality_mapping','approval_rate_projects','approval_rate_mw','approved_projects','total_projects'],
                                            range_color=(0, 1),
                                            zoom=6.37, 
                                            center = {"lat": 38.00692, "lon": -79.40695},
                                            opacity=1,
                                            labels={'approval_rate_projects':'Percent<br>Approved',
                                                    'total_projects':'Cumulative Total Projects',
                                                    'approved_projects':'Cumulative Approved Projects'})
        approvedRateMap.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Project Approval Rate: %{customdata[1]:.0%}<br>Approved Projects: %{customdata[3]}<br>Total Projects: %{customdata[4]}<br><extra></extra>")
        approvedRateMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                                      width=1155,
                                      height=600,
                                      map_style='carto-positron-nolabels',
                                      paper_bgcolor='rgba(0,0,0,0)',
                                      coloraxis_colorbar=dict(tickfont=dict(size=10,
                                                                            color='#242e4c'),
                                                                            orientation="h",
                                                              tickformat='.0%'))
        approvedRateMap.update_geos(fitbounds='locations')
        approvedRateMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)
        return approvedRateMap  

    elif map_type=='deniedRateMap':
        deniedRateMap = px.choropleth_map(statusRate[statusRate['year']==slide_year], 
                                          geojson=counties, 
                                          locations='fips', 
                                          color='denial_rate_projects',
                                          color_continuous_scale=['#F2F4F8','rgb(229, 114, 0)'],
                                          custom_data=['locality_mapping','denial_rate_projects','denial_rate_mw','denied_projects','total_projects'],
                                          range_color=(0, 1),
                                          zoom=6.37, 
                                          center = {"lat": 38.00692, "lon": -79.40695},
                                          opacity=1,
                                          labels={'denial_rate_projects':'Percent<br>Denied',
                                                  'total_projects':'Cumulative Total Projects',
                                                  'denied_projects':'Cumulative Denied Projects'})
        deniedRateMap.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Project Denial Rate: %{customdata[1]:.0%}<br>Denied Projects: %{customdata[3]}<br>Total Projects: %{customdata[4]}<br><extra></extra>")
        deniedRateMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                                    width=1155,
                                    height=600,
                                    map_style='carto-positron-nolabels',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    coloraxis_colorbar=dict(tickfont=dict(size=10,
                                                                          color='#242e4c'),
                                                                          orientation="h",
                                                            tickformat=".0%"))
        deniedRateMap.update_geos(fitbounds='locations')
        deniedRateMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)
        return deniedRateMap

# Define a callback to update the pie graph
@dashappbat.callback(
    Output('graphOne', 'figure'),
    [Input(component_id='graphOneButtons', component_property='value')]
)
def update_pie_chart(value):
    if value=='mwPie':
        return mwPieChart
    elif value=='projectsPie':
        return projectsPieChart
    elif value=='mwhPie':
        return mwhPieChart
    
# Define a callback to update the annual bar graph
@dashappbat.callback(
    Output('graphTwo', 'figure'),
    [Input(component_id='graphTwoButtons', component_property='value')]
)
def update_annual_chart(value):
    if value=='statusLine':
        return rateAnnualLine
    elif value=='rateLine':
        return actionAnnualLine
    elif value=='mwLine':
        return mwAnnualLine
    elif value=='projectsLine':
        return projectsAnnualLine
    elif value=='mwhLine':
        return mwhAnnualLine
    
# Define a callback to update the size bar graph
@dashappbat.callback(
    Output('graphThree', 'figure'),
    [Input(component_id='graphThreeButtons', component_property='value')]
)
def update_status_bar_chart(value):
    if value=='mwStatusBar':
        return mwStatusBar
    elif value=="mwhStatusBar":
        return mwhStatusBar

@dashappbat.callback(
    Output('graphFour', 'figure'),
    [Input(component_id='graphFourButtons', component_property='value')]
)
def update_regional_chart(value):
    if value=='mwRegionalBar':
        return mwRegionalBar
    
if __name__ == '__main__':
    dashappbat.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))