from .models import SolarProjectData, CountyData
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
plotData = SolarProjectData.objects.values('data_id',
                                           'project_name',
                                           'project_mw',
                                           'local_permit_status',
                                           'public_project_acres',
                                           'region',
                                           'phase_mw',
                                           'project_phase',
                                           'final_action_year',
                                           'locality',
                                           'latitude',
                                           'longitude')
#define a base dataframe
df = pd.DataFrame.from_records(plotData)
#data munging to sort out some value inconsistencies and plotting needs
df['project_mw'] = df['project_mw'].replace(np.nan, 0)
df['phase_mw'] = df['phase_mw'].replace(np.nan, 0)
for i in range(0,len(df.index)-1):
    if df.local_permit_status[i] == 'Approved/Amended' and df.project_mw[i]==0:
        df.project_mw[i] = df.phase_mw[i]
for i in range(0,len(df.index)-1):
    if df.local_permit_status[i] == 'Approved' and df.project_mw[i]==0:
        df.project_mw[i] = df.phase_mw[i]
#create the range categories
df['mw_size_range'] = pd.cut(df.project_mw,bins=[0,5,20,150,9999],labels=['≤5MW','5MW< - ≤20MW','20MW< - ≤150MW','150MW<'],include_lowest=True)
df['mw_size_range_int'] = pd.cut(df.project_mw,bins=[0,5,20,150,9999],labels=['1','5','10','25'],include_lowest=True).astype('int')
#define the dataset for the pie charts
pieData = df.groupby('local_permit_status').agg({'project_mw':'sum','phase_mw':'sum','data_id':'count','public_project_acres':'sum'}).reset_index()
#define the data used in the annual line charts, summing the relevant values by year and by status then calculating an annual rate of status action
annualData = pd.DataFrame(df[df["local_permit_status"]!= 'Pending'].groupby(['final_action_year','local_permit_status']).agg({'data_id':'count','project_mw':'sum'}).reset_index())
annualData = annualData.rename(columns={'data_id':'project_count'})
annualTotal = df[df["local_permit_status"]!= 'Pending'].groupby('final_action_year').agg({'data_id':'count'}).reset_index()
annualTotal = annualTotal.rename(columns={'data_id':'annual_total'})
annualData = pd.merge(annualData,annualTotal,on='final_action_year')
annualData['annual_rate'] = round(annualData['project_count']/annualData['annual_total'],2)

#annual action rate data for approved/denied projects
actionRateAnnual = df[df.local_permit_status.isin(["Approved","Denied"])].groupby(["final_action_year","local_permit_status"]).agg({"data_id":"count"}).reset_index().rename(columns={"data_id":"project_count"})
annualActionTotal = actionRateAnnual.groupby("final_action_year").agg({"project_count":"sum"}).reset_index().rename(columns={"project_count":"annual_total"})
actionRateAnnual=pd.merge(actionRateAnnual,annualActionTotal,how="left",on="final_action_year")
actionRateAnnual["action_rate"] = round(actionRateAnnual['project_count']/actionRateAnnual['annual_total'],2)

#define the regional data, straightforward summary of relevant datapoints by region. More could be added
regionalData = pd.DataFrame(df.groupby(['region','local_permit_status']).agg({'project_mw':'sum','data_id':'count','public_project_acres':'sum'}).reset_index())

#define the size category data, summarizing by category
sizeCategoryData = pd.DataFrame(df[df.local_permit_status.isin(["Approved","Approved/Amended","Denied","Withdrawn","By-right"])].groupby(["mw_size_range",'local_permit_status']).agg({'project_mw':'sum','data_id':'count'}).reset_index()).rename(columns={'data_id':'project_count'})
#get the project and megawatt totals by size category
size_summary = sizeCategoryData.groupby('mw_size_range').agg({'project_mw':'sum','project_count':'sum'}).reset_index().rename(columns={'project_mw':'size_total_mw','project_count':'size_total_projects'})
sizeCategoryData = pd.merge(sizeCategoryData,size_summary,how='left',on='mw_size_range')
#calculate the percent of each size category per local permit status (i.e, out of all 150MW projects, what percent have been Approved/Denied/etc.)
sizeCategoryData['percent_of_size_mw'] = sizeCategoryData['project_mw']/sizeCategoryData['size_total_mw']
sizeCategoryData['percent_of_size_projects'] = sizeCategoryData['project_count']/sizeCategoryData['size_total_projects']

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
mapDataClean['final_action_year']=mapDataClean.final_action_year.replace('PENDING',2026)
mapDataClean['final_action_year']=mapDataClean.final_action_year.replace('PENDING  ',2026).astype("int")
years = mapDataClean['final_action_year'].unique()
years.sort()

#MW heatmap dataframe
heatMWYear = mapDataClean[(mapDataClean.local_permit_status.isin(['Approved','Denied'])) & (mapDataClean['final_action_year'].astype("int") <= years[0])].groupby(['local_permit_status','fips','locality_mapping']).agg({'project_mw':'sum','data_id':'count'}).reset_index()
heatMWYear['year']=years[0]

for year in years:
    heatMWYeari = mapDataClean[(mapDataClean.local_permit_status.isin(['Approved','Denied'])) & (mapDataClean['final_action_year'].astype("int") <= year)].groupby(['local_permit_status','fips','locality_mapping']).agg({'project_mw':'sum','data_id':'count'}).reset_index()
    heatMWYeari['year']=year
    heatMWYear = pd.concat([heatMWYear,heatMWYeari])

#action rate heatmap dataframe
actionRate = pd.DataFrame()
for year in years:
    all_fips = pd.DataFrame(mapDataClean[(mapDataClean['final_action_year'] <= year) &(mapDataClean['local_permit_status'] !='PENDING')].groupby(['fips','locality_mapping']).agg({'project_mw':'sum','data_id':'count'}).reset_index()).rename(columns={'project_mw':'total_mw','data_id':'total_projects'})

    approved_fips = pd.DataFrame(mapDataClean[(mapDataClean.local_permit_status == 'Approved') & (mapDataClean['final_action_year'].astype("int")<= year)].groupby(['fips']).agg({'project_mw':'sum','data_id':'count'}).reset_index()).rename(columns={'project_mw':'approved_mw','data_id':'approved_projects'})

    denied_fips = pd.DataFrame(mapDataClean[(mapDataClean.local_permit_status == 'Denied') & (mapDataClean['final_action_year'].astype("int")<= year)].groupby(['fips']).agg({'project_mw':'sum','data_id':'count'}).reset_index()).rename(columns={'project_mw':'denied_mw','data_id':'denied_projects'})
    
    approved = pd.merge(all_fips,approved_fips,how='left',on='fips')
    approved_denied = pd.merge(approved,denied_fips,how='left',on='fips')
    approved_denied['year']=year
    actionRate = pd.concat([actionRate,approved_denied])

actionRate['approved_mw'] = actionRate['approved_mw'].replace(np.nan,0)
actionRate['approved_projects'] = actionRate['approved_projects'].replace(np.nan,0)
actionRate['approval_rate_mw']=round(actionRate['approved_mw']/actionRate['total_mw'],4)
actionRate['approval_rate_projects']=round(actionRate['approved_projects']/actionRate['total_projects'],4)

actionRate['denied_mw'] = actionRate['denied_mw'].replace(np.nan,0)
actionRate['denied_projects'] = actionRate['denied_projects'].replace(np.nan,0)
actionRate['denial_rate_mw']=round(actionRate['denied_mw']/actionRate['total_mw'],4)
actionRate['denial_rate_projects']=round(actionRate['denied_projects']/actionRate['total_projects'],4)



mwPieChart = px.pie(pieData[pieData.local_permit_status != 'NA'],
                    title="<b>Solar Megawatts by Local Permit Status</b>",
                    values='project_mw', 
                    names='local_permit_status', 
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
                    labels={'local_permit_status':'Local Permit Status',
                            'project_mw':'Megawatts',
                            'data_id':'Project Count'},
                    hover_name='local_permit_status',
                    hover_data={'local_permit_status':False})
     
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

     
projectsPieChart= px.pie(pieData[pieData.local_permit_status != 'NA'], 
                         values='data_id', 
                         names='local_permit_status', 
                         title="<b>Solar Projects by Local Permit Status</b>",
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
                         labels={'local_permit_status':'Local Permit Status',
                                 'data_id':'Total Projects'},
                         hover_name='local_permit_status',
                         hover_data={'local_permit_status':False})
     
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

    
acrePieChart = px.pie(pieData[pieData.local_permit_status != 'NA'], 
                      values='public_project_acres', 
                      names='local_permit_status', 
                      title="<b>Solar Acres by Local Permit Status</b>",
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
                      labels={'local_permit_status':'Local Permit Status',
                              'public_project_acres':'Project Acres'},
                      hover_name='local_permit_status',
                      hover_data={'local_permit_status':False})
     
acrePieChart.update_layout(margin=dict(l=5, r=5, t=100, b=0),
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
     
acrePieChart.update_traces(texttemplate="%{value:,.3s} (%{percent:.1%}) ",hovertemplate='<b>%{label}</b><br>Project Acres (Best Available Estimate): %{value:,.0f}<br>Percent of Total Acres: %{percent:.1%}')

rateAnnualLine = px.line(annualData[(annualData['final_action_year'] != 'PENDING') & (annualData['local_permit_status'] != 'NA')],  
                         x="final_action_year", 
                         y='annual_rate',
                         color='local_permit_status',
                         title="<b>Annual Solar Local Status Rate</b>",
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
                                 'annual_rate':'Rate',
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

actionAnnualLine = px.line(actionRateAnnual,  
                         x="final_action_year", 
                         y='action_rate',
                         color='local_permit_status',
                         title="<b>Annual Solar Action Rate</b>",
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
                             hovertemplate='<b>%{customdata[0]}</b><br>Year: %{x}<br>Percent %{customdata[0]}: %{y}<br>%{customdata[0]} Projects: %{customdata[1]}<br>Total Projects Acted On: %{customdata[2]}<br><extra></extra>')

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

mwAnnualLine = px.line(annualData[(annualData['final_action_year'] != 'PENDING') & (annualData['local_permit_status'] != 'NA')],
                       x="final_action_year", 
                       y="project_mw",
                       color='local_permit_status',
                       title="<b>Annual Solar Megawatts by Local Permit Status</b>",
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
                                'project_mw':'Megawatts'})
     
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

projectsAnnualLine = px.line(annualData[(annualData['final_action_year'] != 'PENDING') & (annualData['local_permit_status'] != 'NA')],
                             x="final_action_year", 
                             y="project_count",
                             color='local_permit_status',
                             title="<b>Annual Solar Projects by Local Permit Status</b>",
                             custom_data=['local_permit_status','project_mw'],
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


mwRegionalBar = px.bar(regionalData[regionalData['local_permit_status'] != 'NA'], 
                       x="region", 
                       y='project_mw', 
                       color='local_permit_status',
                       title="<b>Regional Megawatts by Local Permit Status</br>",
                       custom_data=['local_permit_status','public_project_acres','data_id'],
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
                              'project_mw':'Megawatts',
                              'public_project_acres':'Project Acreage',
                              'data_id':'Project Count',
                              'local_permit_status':'Local Permit Status'},
                      barmode='stack')
mwRegionalBar.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Region: %{x}<br>%{customdata[0]} Megawatts: %{y}<br>%{customdata[0]} Projects: %{customdata[2]}<br>%{customdata[0]} Project Acres (Best Available Estimate): %{customdata[1]:,.0f}<br><extra></extra>")

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
     


sizeMWBar = px.bar(sizeCategoryData[sizeCategoryData['local_permit_status'].isin(["Approved","Denied",'Withdrawn'])], 
                   title="<b>Solar Megawatts by Project Size</b>",
                   x="mw_size_range", 
                   y="project_mw",
                   color='local_permit_status',
                   custom_data=['local_permit_status','project_count'],
                   height=585,
                   width=480,
                   color_discrete_sequence=['rgb(40, 67, 118)', 
                                            'rgb(229, 114, 0)',
                                            'rgb(200, 203, 210)'],
                   barmode='group',
                   labels={'mw_size_range':'Megawatt Range',
                           'local_permit_status':'Local Permit Status',
                           'project_mw':'Megawatts'})

sizeMWBar.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Project Megawatt Range: %{x}<br>Megawatts: %{y:,.0f}<br>Projects: %{customdata[1]}<br><extra></extra>")

sizeMWBar.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                        paper_bgcolor='#F2F4F8',
                        plot_bgcolor='#F2F4F8',
                        legend=dict(font=dict(size=10,
                                              color='#242e4c'),
                                    orientation='h',
                                    yanchor="bottom",
                                    y=.95,
                                    x=0,
                                    title=''),
                        font=dict(size=10,
                                  color='#242e4c'),
                        font_family='franklin-gothic-urw-cond, sans-serif',
                        title=dict(font=dict(size=22), automargin=False, yref='paper'),
                        title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                        xaxis=dict(tickmode='array',
                                   tickvals=['≤5MW','5MW< - ≤20MW','20MW< - ≤150MW','150MW<'],
                                   title=''),
                        yaxis=dict(tickformat=",.0f",
                                   title='Megawatts'))



sizeProjectsBar = px.bar(sizeCategoryData[sizeCategoryData['local_permit_status'].isin(["Approved","Denied",'Withdrawn'])], 
                         x="mw_size_range", 
                         y='project_count',
                         color='local_permit_status',
                         title="<b>Solar Projects by Project Size</b>",
                         custom_data=['local_permit_status','project_mw'],
                         height=585,
                         width=480,
                         color_discrete_sequence=['rgb(40, 67, 118)', 
                                                  'rgb(229, 114, 0)',
                                                  'rgb(200, 203, 210)'],
                         labels={'project_count':'Project Count',
                                 'mw_size_range':'Megawatts',
                                 'local_permit_status':'Local Permit Status'},
                         barmode='group',
                         hover_name='local_permit_status',
                         hover_data={'local_permit_status':False})

sizeProjectsBar.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Project Megawatt Range: %{x}<br>Projects: %{y}<br>Megawatts: %{customdata[1]:,.0f}<br><extra></extra>")

sizeProjectsBar.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                              paper_bgcolor='#F2F4F8',
                              plot_bgcolor='#F2F4F8',
                              legend=dict(font=dict(size=10,
                                                    color='#242e4c'),
                                          orientation='h',
                                          yanchor="bottom",
                                          y=.95,
                                          x=0,
                                          title=''),
                              font=dict(size=10,
                                        color='#242e4c'),
                              font_family='franklin-gothic-urw-cond, sans-serif',
                            title=dict(font=dict(size=22), automargin=False, yref='paper'),
                            title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                              yaxis=dict(title="Projects"),
                              xaxis=dict(tickmode='array',
                                         tickvals=['≤5MW','5MW< - ≤20MW','20MW< - ≤150MW','150MW<'],
                                         title=''))



#graphing the percent of projects in each size category by decision category
sizePercentBar = px.bar(sizeCategoryData[(sizeCategoryData.local_permit_status != "Pending") & (sizeCategoryData.local_permit_status != 'NA')],
                        color='local_permit_status',
                        custom_data=['project_count','local_permit_status','project_mw'],
                        #text_auto=True,
                        title="<b>Local Permit Status Percent of Projects by Size </b>",
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
                        labels={'mw_size_range':'Project Size',
                                'local_permit_status':'Local Permit Status',
                                'percent_of_size_projects':'Percent of Size Range Projects',
                                'project_count':"Project Count"
                                },
                        x='mw_size_range',
                        y='percent_of_size_projects',
                        height=585,
                        width=480,
                        barmode='stack')
sizePercentBar.update_traces(hovertemplate="<b>%{x}</b><br>Local Permit Status: %{customdata[1]}<br>Percent of Projects in Size Range: %{y}<br>Projects: %{customdata[0]}<br>Megawatts: %{customdata[2]:,.0f}<br><extra></extra>")
sizePercentBar.update_layout(margin=dict(l=5, r=5, t=100, b=0),
                                paper_bgcolor='#F2F4F8',
                                plot_bgcolor='#F2F4F8',
                                yaxis=dict(tickformat='.0%'),
                                xaxis=dict(title=''),
                                font_family='franklin-gothic-urw-cond, sans-serif',
                                font=dict(size=10,
                                  color='#242e4c'),
                                title=dict(font=dict(size=20), automargin=False, yref='paper'),
                                title_subtitle=dict(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>', font=dict(size=10)),
                     legend=dict(font=dict(size=10,
                                              color='#242e4c'),
                                    orientation='h',
                                    yanchor="bottom",
                                    y=.95,
                                    x=0,
                                    title=''))

dashapp = DjangoDash(name='SolarDash',add_bootstrap_links=True, external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.FLATLY,'/static/css/styles.css'])

dashapp.layout =  dbc.Container([
    #buid the state overview page
    html.Div([
        html.Br(),
        html.Br(),
        html.H1("Virginia Solar Dashboard"),
        html.P("Visualizations reflect all projects in the database as of December 31, 2025. Explore different data highlights with the buttons, and download a graph with the camera icon in the upper right corner of each graph. Project Size map includes all projects regardless of local permit status. Hovertext labels on all maps and graphs provide supplemental information."),
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
                {"label": "Local Permit Status", "value": 'statusPermitMap'},
                {"label": "Project Size", "value": 'sizeMap'}, 
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
                {"label": "Megawatts", "value": 'mwPie'}, 
                {"label": "Projects", "value": 'projectsPie'},
                {"label": "Best Available Acres", "value": 'acresPie'}
            ],
        value='mwPie'
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
                {"label": "Megawatts", "value": 'sizeMWBar'}, 
                {"label": "Projects", "value": 'sizeProjectsBar'},
                {"label": "Local Status Rate", "value": 'sizePercentBar'}
                
            ],
        value='sizeMWBar'
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
                {"label": "Local Status Rate", "value": 'rateLine'},
                {"label": "Action Rate", "value": 'actionLine'},
                {"label": "Megawatts", "value": 'mwLine'}, 
                {"label": "Projects", "value": 'projectsLine'}
            ],
        value='rateLine'
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
            'margin-top': 50,
            'margin-right': 0,
            'margin-left':10,
            'margin-bottom': 35,
            'display': 'flex',
            'background-color':'#F2F4F8'
        })])],
                            fluid=True,
                            style={'display': 'flex',
                                   'background-color':'#F2F4F8'},
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

@dashapp.callback(
        Output("stateMap", "figure"),
        Input("mapButtons","value"),
        Input("years", "value"))

def update_map(map_type,slide_year):
    if map_type=='statusPermitMap':
        statusMap = px.scatter_map(
            mapDataClean[mapDataClean['final_action_year'] <= slide_year],
            color='local_permit_status',
            custom_data=['project_name','locality','local_permit_status','mw_size_range','final_action_year','project_mw','public_project_acres'],
            color_discrete_sequence=['rgb(40, 67, 118)', 'rgb(253, 218, 36)', 'rgb(229, 114, 0)', 'rgb(200, 203, 210)','rgb(37, 202, 211)','rgb(98, 187, 70)'],
            category_orders={"local_permit_status": ["Approved", "Approved/Amended", "Denied", "Withdrawn", "By-right", "Pending"]},
            labels={'locality':'Locality',
                    'local_permit_status':'Local Permit Status',
                    'project_mw':'Project Megawatts',
                    'project_name':'Project Name',
                    'project_phase':'Phase Name',
                    'phase_mw':'Phase Megawatts',
                    'final_action_year':'Year',
                    'locality': 'Locality'},
                    hover_name='project_name',
                    hover_data={'final_action_year':True,
                                    'project_mw': True,
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
                    paper_bgcolor='#F2F4F8',
                    xaxis=dict(showgrid=False,
                            zeroline=False,
                            visible=False),
                    yaxis=dict(showgrid=False,
                             zeroline=False,
                            visible=False),
                )
        statusMap.update_traces(marker=dict(size=10),
                                    hovertemplate="<b>%{customdata[0]}</b><br>Locality: %{customdata[1]}<br>Local Permit Status: %{customdata[2]}<br>Project Megawatts: %{customdata[5]:,.0f}<br>Year: %{customdata[4]}<br>Best Available Project Acreage: %{customdata[6]:,.0f}<br><extra></extra>")
        statusMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)


        return statusMap
    
    elif map_type=='sizeMap':
        sizeMap = px.scatter_map(
                mapDataClean[mapDataClean['final_action_year'] <= slide_year],
                color='mw_size_range',
                custom_data=['project_name','locality','local_permit_status','mw_size_range','final_action_year','project_mw','public_project_acres'],
            #color_discrete_sequence=['rgb(229, 114, 0)','rgb(253, 218, 36)', 'rgb(40, 67, 118)', 'rgb(98, 187, 70)'],
                color_discrete_sequence=['rgb(40, 67, 118)', 
                                      #'rgb(253, 218, 36)', 
                                      'rgb(229, 114, 0)',
                                      'rgb(200, 203, 210)',
                                      'rgb(37, 202, 211)',
                                      'rgb(98, 187, 70)'],
                category_orders={"mw_size_range": ['≤5MW','5MW< - ≤20MW','20MW< - ≤150MW','150MW<']},
                labels={'locality':'Locality',
                    'local_permit_status':'Local Permit Status',
                    'project_mw':'Project Megawatts',
                    'project_name':'Project Name',
                    'project_phase':'Phase Name',
                    'phase_mw':'Phase Megawatts',
                    'final_action_year':'Year',
                    'mw_size_range':'Project Size Category'},
                size='mw_size_range_int',
                lat='latitude',
                lon='longitude',
                zoom=6.57, 
                center = {"lat": 38.00692, "lon": -79.40695},
                )
        sizeMap.update_layout(
                    font=dict(color='#242e4c'),
                    legend=dict(font=dict(size=12,
                                      color='#242e4c'),
                            orientation='h',
                            yanchor='bottom',y=1),
                    margin={"r":0,"t":10,"l":0,"b":0},
                    width=1155,
                    height=600,
                    map_style='carto-positron-nolabels',
                    paper_bgcolor='#F2F4F8')
        
        sizeMap.update_traces(marker=dict(sizeref=.04),
                              hovertemplate="<b>%{customdata[0]}</b><br>Locality: %{customdata[1]}<br>Local Permit Status: %{customdata[2]}<br>Project Size Category: %{customdata[3]}<br>Project Megawatts: %{customdata[5]:,.0f}<br>Year: %{customdata[4]}<br>Best Available Project Acreage: %{customdata[6]:,.0f}<br><extra></extra>")
        sizeMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)

        return sizeMap
    
    elif map_type=='approvedMWMap':
        approvedMWMap = px.choropleth_map(heatMWYear[(heatMWYear['local_permit_status']=='Approved') & (heatMWYear['year']==slide_year)],
                                         geojson=counties, 
                                         locations='fips', 
                                         color='project_mw',
                                         custom_data=['locality_mapping','project_mw','data_id'],
                                         color_continuous_scale=['#F2F4F8','rgb(40, 67, 118)'],
                                         range_color=(0, 500),
                                         zoom=6.37, center = {"lat": 38.00692, "lon": -79.40695},
                                         opacity=1,
                                         labels={'project_mw':'Approved<br>Megawatts',
                                                 'data_id':'Number of Projects'})
        approvedMWMap.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Approved Megawatts: %{customdata[1]:,.0f}<br>Approved Projects: %{customdata[2]:,.0f}<br><extra></extra>")
        approvedMWMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                        width=1155,
                        height=600,
                        map_style='carto-positron-nolabels',
                        paper_bgcolor='#F2F4F8',
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
                                        color='project_mw',
                                        custom_data=['locality_mapping','project_mw','data_id'],
                                        color_continuous_scale=['#F2F4F8','rgb(229, 114, 0)'],
                                        range_color=(0, 500),
                                        zoom=6.37, center = {"lat": 38.00692, "lon": -79.40695},
                                        opacity=1,
                                        labels={'project_mw':'Denied<br>Megawatts',
                                                'data_id':'Number of Projects'})
        deniedMWMap.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Denied Megawatts: %{customdata[1]:,.0f}<br>Denied Projects: %{customdata[2]:,.0f}<br><extra></extra>")
        deniedMWMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                                  width=1155,
                                  height=600,
                                  map_style='carto-positron-nolabels',
                                  paper_bgcolor='#F2F4F8',
                                  coloraxis_colorbar=dict(tickfont=dict(size=10,color='#242e4c'),orientation='h'))
        deniedMWMap.update_coloraxes(colorbar_labelalias={500:'500 and above'})
        deniedMWMap.update_geos(fitbounds='locations')
        deniedMWMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)
        return deniedMWMap
    elif map_type=='approvedRateMap':
        approvedRateMap = px.choropleth_map(actionRate[actionRate['year']==slide_year], 
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
                                      paper_bgcolor='#F2F4F8',
                                      coloraxis_colorbar=dict(tickfont=dict(size=10,
                                                                            color='#242e4c'),
                                                                            orientation="h",
                                                              tickformat='.0%'))
        approvedRateMap.update_geos(fitbounds='locations')
        approvedRateMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)
        return approvedRateMap  

    elif map_type=='deniedRateMap':
        deniedRateMap = px.choropleth_map(actionRate[actionRate['year']==slide_year], 
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
                                    paper_bgcolor='#F2F4F8',
                                    coloraxis_colorbar=dict(tickfont=dict(size=10,
                                                                          color='#242e4c'),
                                                                          orientation="h",
                                                            tickformat=".0%"))
        deniedRateMap.update_geos(fitbounds='locations')
        deniedRateMap.add_annotation(text='<i>Source: Weldon Cooper Center Virginia Solar and Storage Database</i>',x=0,y=0,xref="paper", yref="paper",font=dict(size=8),showarrow=False)
        return deniedRateMap

# Define a callback to update the pie graph
@dashapp.callback(
    Output('graphOne', 'figure'),
    [Input(component_id='graphOneButtons', component_property='value')]
)
def update_pie_chart(value):
    if value=='mwPie':
        return mwPieChart
    elif value=='projectsPie':
        return projectsPieChart
    elif value=='acresPie':
        return acrePieChart
    
# Define a callback to update the annual bar graph
@dashapp.callback(
    Output('graphTwo', 'figure'),
    [Input(component_id='graphTwoButtons', component_property='value')]
)
def update_annual_chart(value):
    if value=='rateLine':
        return rateAnnualLine
    elif value=='actionLine':
        return actionAnnualLine
    elif value=='mwLine':
        return mwAnnualLine
    elif value=='projectsLine':
        return projectsAnnualLine
    
# Define a callback to update the size bar graph
@dashapp.callback(
    Output('graphThree', 'figure'),
    [Input(component_id='graphThreeButtons', component_property='value')]
)
def update_size_chart(value):
    if value=='sizeMWBar':
        return sizeMWBar
    elif value=='sizeProjectsBar':
        return sizeProjectsBar
    elif value=='sizePercentBar':
        return sizePercentBar
    
@dashapp.callback(
    Output('graphFour', 'figure'),
    [Input(component_id='graphFourButtons', component_property='value')]
)
def update_size_chart(value):
    if value=='mwRegionalBar':
        return mwRegionalBar
    
if __name__ == '__main__':
    dashapp.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))