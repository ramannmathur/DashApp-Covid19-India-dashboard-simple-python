# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 21:41:01 2020

@author: Raman
"""



from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import numpy as np
SPREADSHEET_ID = # i of your google sheed
RANGE_NAME = #name of worskspace


def get_google_sheet(spreadsheet_id, range_name):
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    # Setup the Sheets API
    store = file.Storage(#location of json credentials )
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    gsheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return gsheet


def gsheet2df(gsheet):
    """ Converts Google sheet data to a Pandas DataFrame.
    Note: This script assumes that your data contains a header file on the first row!
    Also note that the Google API returns 'none' from empty cells - in order for the code
    below to work, you'll need to make sure your sheet doesn't contain empty cells,
    or update the code to account for such instances.
    """
    header = gsheet.get('values', [])[1]   # Assumes first line is header!
    values = gsheet.get('values', [])[2:]  # Everything else is data.
    if not values:
        print('No data found.')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                column_data.append(row[col_id])
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        return df


gsheet = get_google_sheet(SPREADSHEET_ID, RANGE_NAME)
df = gsheet2df(gsheet)
print('Dataframe size = ', df.shape)

df.columns=['State','Confirmed','Recovered','Deaths','Active','Last_Updated_Time','State_code','Delta_Confirmed','Delta_Recovered','Delta_Deaths']
print(df.head())
df.drop(["Last_Updated_Time","State_code","Delta_Confirmed","Delta_Recovered","Delta_Deaths"],axis=1,inplace = True)
print(df.head())
total=df['Confirmed'].sum()
df1=pd.read_csv('https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv')
df2=pd.read_csv('https://api.covid19india.org/csv/latest/raw_data.csv')
df3=df2.Gender[df2.Gender=='M']
df4=df2.Gender[df2.Gender=='F']
df5=pd.read_csv('https://api.covid19india.org/csv/latest/case_time_series.csv')
df6=pd.read_csv('C:/Users/venv/state_wise.csv')
def generate_table(dataframe, max_rows=500):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

mgr_options = df["State"].unique()
figure=go.Figure()
#app = dash.Dash()

app.layout = html.Div(children=[
    html.H4(children='Covid19 India Dashboard',style={"color":"red"}),
    generate_table(df),  dcc.Graph(
                    id='example-graph-3',
                    figure={
                        'data': [
                            {'x': df['State'], 'y': df['Confirmed'], 'type': 'bar', 'name': 'Confirmed'},
                            {'x': df['State'], 'y': df['Active'], 'type': 'bar', 'name': u'Active'},
                            {'x': df['State'], 'y': df['Recovered'], 'type': 'bar', 'name': u'Recovered'},
                            {'x': df['State'], 'y': df['Deaths'], 'type': 'bar', 'name': u'Deaths'},
                        ],
                        'layout': {
                            'title': 'State Wise Cases',
                            'xaxis' : dict(
                                title='x Axis',
                                titlefont=dict(
                                family='Courier New, monospace',
                                size=20,
                                color='#7f7f7f'
                            )),
                            'yaxis' : dict(
                                title='y Axis',
                                titlefont=dict(
                                family='Helvetica, monospace',
                                size=20,
                                color='#7f7f7f'
                            ))
                        }
                    }
                ),

       html.Div(
            [
            html.Div([
                dcc.Graph(
                    id='example-graph',
                    figure=px.density_mapbox(df6, lat='lat', lon='long', z='Confirmed', radius=10,
                        center=dict(lat=20.5937, lon=78.9629), zoom=4,
                        mapbox_style="stamen-terrain"),
                    #fig.update_traces(textposition='inside'),
                    #fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide'),
    
    
                )
                ], className= 'six columns'
                ),

                html.Div([
                dcc.Graph(
                    id='example-graph-2',
                    figure={
                        'data': [
                            {'x': df1['State'], 'y': df1['Total Tested'], 'type': 'histogram', 'name': 'Total Tested'},
                            {'x': df1['State'], 'y': df1['Positive'], 'type': 'histogram', 'name': u'Positive'},
                            {'x': df1['State'], 'y': df1['Negative'], 'type': 'histogram', 'name': u'Negative'},
                        ],
                        'layout': {
                            'title': 'Total Tested'
                        }
                    }
                ),dcc.Graph(
                    id='example-graph-4',
                    figure={
                        'data': [
                            #{'x':['Male Infected','Female Infected'], 'y': [df3.count(),df4.count()], 'type': 'pie', 'name': 'Total Tested'},
                            {'values': [df3.count(),df4.count()],'labels':['Male Infected','Female Infected'],'type': 'pie'},
                            
                        ],
                        'layout': {
                            'title': 'Gender Distribution'
                        }
                    }
                ),dcc.Graph(figure=px.line(df5, x='Date', y='Daily Confirmed')),dcc.Graph(figure=px.line(df5, x='Date', y='Total Confirmed')),dcc.Graph(figure=px.line(df5, x='Date', y='Total Deceased')),
                ], className= 'nine columns'
                )
            ], className="row"
        )
    ], className='ten columns offset-by-one')
if __name__ == '__main__':
    app.run_server(debug=True)