## Host dummy functions for developemt only
import time
import random
import datetime
from plotly import graph_objs as go

import streamlit as st

@st.cache(show_spinner=False)
def get_data(mrn):
    time.sleep(1)
    dummy_current = 0
    dummy_data = [dummy_current]
    for _ in range(23):
        dummy_current += random.randint(3, 14)*1000
        dummy_data.append(dummy_current)
    return dummy_data

@st.cache(show_spinner=False)
def run_inference(patient_data):
    time.sleep(3)
    _base = patient_data["meta"][-1]
    def cumulative(base, array):
        new_array=[] 
        j=0
        for i in range(0,len(array)):
            j+=array[i]
            new_array.append(base+j)
        return new_array
     
    return {k:cumulative(_base, [random.randint(30, 90)*1000 for _ in range(6)]) for k in patient_data["pathways"]}

@st.cache(show_spinner=False)
def get_predictions_plot(patient_data, preditions):
    x_size = len(patient_data["meta"])
    today = datetime.datetime.today()
    x_dates = list([datetime.timedelta(days=x*30)+today for x in range(1,7)])
    x_dates = [x.date() for x in x_dates]
    date_3m_later = today+datetime.timedelta(days=30)

    fig = go.Figure()
    fig.add_traces([
        go.Scatter(
            x = x_dates,
            y = preditions[k],
            mode="lines",
            name = k,
            text = [k]*len(x_dates),
            hovertemplate =
            '<br><b>Pathway</b>: %{text}<br>'+
            '<b>Date</b>: %{x}<br>'+
            '<b>Margin</b>: %{y}'+
            '<extra></extra>',
            ) 
        for k in sorted(preditions.keys())
    ])
    fig.layout.xaxis.title= "Date"
    fig.layout.yaxis.title= "Cumulative Pharmacy Margin"
    fig.layout.plot_bgcolor='rgba(0,0,0,0)'

    fig.update_yaxes(
        tickprefix="$",rangemode="nonnegative", 
        linecolor="black",tickcolor="black", ticks='inside',)
    
    fig.update_layout(
        xaxis = dict(
            range = [x_dates[0]-datetime.timedelta(days=14), x_dates[-1] + datetime.timedelta(days=14)], 
            linecolor = "black", tickcolor="black", ticks='inside',
            )
        )
    return fig