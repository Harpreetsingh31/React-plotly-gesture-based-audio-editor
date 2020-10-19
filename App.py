# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 14:00:36 2020
@author: harpreet
"""
#conda install -c conda-forge pydub
#conda install -c anaconda pyaudio
#conda install -c anaconda pillow
#conda install -c conda-forge ffmpeg

import pyaudio
import pydub
from pydub import AudioSegment
from pydub.playback import play
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw
import numpy as np
import os,sys
from os.path import isfile, join
import pandas as pd
import copy
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

import base64

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
PATHWAY = r"C:\Users\harpr\Downloads\audioedit\Data"
files = [f for f in os.listdir(PATHWAY) if isfile(join(PATHWAY, f))]

app    = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server
  
data = []

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    color='Orange',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis = {'showgrid': False,'zeroline':False},
    yaxis = {'showgrid': False,'visible': False},
    
    legend=dict(font=dict(size=10), orientation="h"),
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

def make_count_figure(df):

    layout_count = copy.deepcopy(layout)
    data = [
        dict(
            type="Scatter",
            mode="markers",
            x=df.time,
            y=df["Amplitude"] / 2,
            name="Amplitude",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=df.time,
            y=df["Amplitude"],
            name="Amplitude",
        ),
    ]

    #layout_count["title"] = "Completed Wells/Year"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure

def make_count_figure2(df,input1,input2):

    layout_count = copy.deepcopy(layout)
    
    colors = []
    for i in range(0, 300):
        if i >= int(input1) and i < int(input2):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(100, 190, 280)")
            
    data = [
        dict(
            type="Scatter",
            mode="markers",
            x=df.time,
            y=df["Amplitude"] / 2,
            name="Amplitude",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=df.time,
            y=df["Amplitude"],
            name="Amplitude",
        ),
    ]

    #layout_count["title"] = "Completed Wells/Year"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure

app.layout = html.Div([
    
    html.Br(),
    html.H1("React_Plotly gesture based Audio editor",style={'height': '20px','width': '40%','margin':'auto','color': 'Black'},),
    html.H6(id="text",), 
    html.Br(),
    
    html.H4("Select a sound:",style={'height': '20px','width': '25%','margin':'auto'},),
    dcc.Dropdown(id='filename',options=[{'label': i, 'value': i} for i in files],value=files[0],
                 style={'height': '20px','width': '50%','margin':'auto'}),
    html.Br(),
    html.Div(id='filename-container',style={'height': '20px','width': '20%','margin':'auto'}),
    
    html.Div([
        dcc.Graph(id="count_graph",style={'height': '250px','width': '100%','margin':'auto'})],
        id="countGraphContainer",className="pretty_container",),
    
    html.Div([  
    html.Label('Start'),
    dcc.Input(id = "start",placeholder = "Enter start time...", type = "number",debounce=True,value = 0),
    html.Label('End'),
    dcc.Input(id = "end",  placeholder = "Enter End time...", type = "number",debounce=True,value = 30)    
    ],style={'height': '20px','width': '30%','margin':'auto'}),
    
    html.Br(),

    html.Div([
    html.Button('Select',id='btn-select'),
    html.Button('Clear' ,id='btn-clear'),     
    ],style={'height': '20px','width': '10%','margin':'auto'}),

    html.Br(),

    html.Div([   
    html.Button('Submit',id='btn-submit'),
    ],style={'height': '20px','width': '5%','margin':'auto'}),
  
    html.Br(),
    
    html.Div([
    html.Div(id='output-select'),
    html.Div(id='output-clear'),
    ],style={'height': '20px','width': '20%','margin':'auto'}),

    #html.Ul([html.Li(x) for x in data]),
    
    html.Br(),
    html.Audio(id="player", controls=True, style={"width": "100%",'margin':'auto'}),
    html.Div(id="output-clientside"),

    html.Div([
        html.H2("Selected Clip",style={'height': '20px','width': '10%','margin':'auto','color': 'Black'},),

        dcc.Graph(id="count_graph_2",style={'height': '150px'})],
        id="countGraphContainer_2",className="pretty_container",),  
    html.Audio(id="player2", controls=True, style={"width": "100%"}),

    
    html.Div([
       html.H2("Final (edited) Sound",style={'height': '20px','width': '15%','margin':'auto','color': 'Black'},),

        dcc.Graph(id="count_graph_3",style={'height': '150px'})],
        id="countGraphContainer_3",className="pretty_container",),
    html.Audio(id="player3", controls=True, style={"width": "100%"}),

    #hidden-div
    html.Div(id='fileplotdata', style={'display': 'none'}),
    html.Div(id='intermediate-value', style={'display': 'none'}),
    html.H6(id="well_text", style={"display": "none"}), 

])
    
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")])

@app.callback(Output('filename-container', 'children'),
              [Input('filename', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)

@app.callback(Output("fileplotdata", "children"),
              [Input('filename', 'value')])
def update_output(value):
    
    #loading any mp3 audio song
    path =  "Data/" + value
    audio= AudioSegment.from_mp3(path)
    AUDIO_LENGTH = audio.duration_seconds
    
    #obtaining raw_data from mp3 for plotting songs waveform
    data2 = np.fromstring(audio._data, np.int16)
    #audio song aplitude data
    df2 = pd.DataFrame({'Amplitude': data2,'indexx':np.arange(0,data2.size)})
    df = df2.sample(int(AUDIO_LENGTH)).sort_values(by='indexx', ascending=True)
    df["time"]= np.linspace(0, AUDIO_LENGTH, num=int(AUDIO_LENGTH))

    return df.to_json(date_format='iso', orient='split')

@app.callback(Output("count_graph", "figure"),
              [Input('fileplotdata', 'children')],
              state=[State('start', 'value'),
                     State('end', 'value')])
def update_graph(jsonified_plot_data,input1,input2):

    df = pd.read_json(jsonified_plot_data, orient='split')
    return make_count_figure2(df,input1,input2)

@app.callback(Output("well_text", "children"),
              [Input("count_graph", "selectedData")])
def update_year_slider(graph_selected):
    
    if graph_selected is None:
        return [0, 30]
    nums = [int(point["pointNumber"]) for point in graph_selected["points"]]
    return [min(nums),max(nums)]

# Slider -> count graph
@app.callback([Output("start", "value"),
               Output("end", "value")],
              [Input("well_text", "children")])
def update_year_slider(graph_selected):
    return graph_selected[0],graph_selected[1]

@app.callback(Output('output-select', 'children'),
              [Input('btn-select', 'n_clicks')],
              state=[State('start', 'value'),
                     State('end', 'value')])
def compute(n_clicks, input1,input2):    
    if (input1 in data):
        data.sort()
        return data
    elif (input1>input2):
        return data
    #elif all(i > input1 for i in data):
     #   return data
    else:
        data.append(input1)
        data.append(input2)
        data.sort()
        return 'Selected Time_slots: {}'.format(data)

@app.callback(Output('output-clear', 'children'),
              [Input('btn-clear', 'n_clicks')] )
def compute(n_clicks):
    del data[-2:]
    return 'Selected Time_slots: {}'.format(data)

    
@app.callback(Output("player", "src"),
              [Input('filename', 'value')])
def update_output(value):
    
    #loading any mp3 audio song
    path =  "Data/" + value
    encoded_sound = base64.b64encode(open(path, 'rb').read())   
    src = 'data:audio/mpeg;base64,{}'.format(encoded_sound.decode())
    return src

@app.callback(Output('intermediate-value', 'children'), 
              [Input('fileplotdata', 'children'),
               Input("well_text", "children")])
def update_graph(jsonified_plot_data,graph_selected):
    
    df = pd.read_json(jsonified_plot_data, orient='split')    
    filtered_df = df[graph_selected[0]:graph_selected[1]]   
    return filtered_df.to_json(date_format='iso', orient='split')

@app.callback([Output("player2", "src"),
               Output('count_graph_2', 'figure')], 
              [Input('intermediate-value', 'children'),
              Input('filename', 'value')],
              state=[State('start', 'value'),
                     State('end', 'value')])
def update_graph(jsonified_cleaned_data,value,input1,input2):
    
        #loading any mp3 audio song
    path =  "Data/" + value
        #path =  "No_Time.mp3"
    sound = AudioSegment.from_mp3(path)
    sound_clip = sound[input1*1000:input2*1000]
        
    name =  "clip_" + value
    sound_clip.export(name, format="mp3")

    encoded_sound = base64.b64encode(open(name, 'rb').read())   
    src = 'data:audio/mpeg;base64,{}'.format(encoded_sound.decode())

    df2 = pd.read_json(jsonified_cleaned_data, orient='split')
    return src,make_count_figure(df2)

@app.callback([Output("player3", "src"),Output('count_graph_3', 'figure')],
              [Input("btn-submit", "n_clicks"),
               Input("well_text", "children"),
              Input('filename', 'value')])
def update_output(submit,graph_selected,value):
    
    if submit:
            #loading any mp3 audio song
        path =  "Data/" + value
        #path =  "No_Time.mp3"
        sound = AudioSegment.from_mp3(path)
        AUDIO_LENGTH = sound.duration_seconds

        sound_filename = sound[0:10]
        newdata = data.copy()
        newdata.append(AUDIO_LENGTH)
        for x in range(1, len(newdata), 2):
            sound_filename +=sound[newdata[x]*1000:newdata[x+1]*1000]
    
        # Concatenation is just adding
        #sound_filename = first_half+second_half
        name = "edited_"+value
        sound_filename.export(name, format="mp3")

        encoded_sound = base64.b64encode(open(name, 'rb').read())
        src = 'data:audio/mpeg;base64,{}'.format(encoded_sound.decode())
        
        audio= sound_filename
        AUDIO_LENGTH = audio.duration_seconds
    
        #obtaining raw_data from mp3 for plotting songs waveform
        data2 = np.fromstring(audio._data, np.int16)
        #audio song aplitude data
        df2 = pd.DataFrame({'Amplitude': data2,'indexx':np.arange(0,data2.size)})
        df = df2.sample(int(AUDIO_LENGTH)).sort_values(by='indexx', ascending=True)
        df["time"]= np.linspace(0, AUDIO_LENGTH, num=int(AUDIO_LENGTH))
        fig = make_count_figure(df)
    
        return src,fig


# Main
if __name__ == "__main__":
    app.run_server(port=8051, debug=False,dev_tools_ui=False,dev_tools_props_check=False)
