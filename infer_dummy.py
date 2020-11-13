## Host dummy functions for developemt only
import time
import random
import datetime
from plotly import graph_objs as go

import streamlit as st

@st.cache(show_spinner=False)
def get_data(length=23):
    time.sleep(1)
    dummy_current = 0
    dummy_data = [dummy_current]
    for _ in range(length):
        dummy_current += random.randint(3, 14)*1000
        dummy_data.append(dummy_current)
    return dummy_data

@st.cache(show_spinner=False)
def run_inference(patient_data):
    time.sleep(3)
    _base = patient_data["meta"][-1]
    return {k:_base + random.randint(30, 90)*1000 for k in patient_data["pathways"]}

@st.cache(show_spinner=False)
def get_predictions_plot(patient_data, preditions):
    x_size = len(patient_data["meta"])
    today = datetime.datetime.today()
    x_dates = list([datetime.timedelta(days=x*14)+today for x in range(1-x_size,1,1)])
    date_3m_later = today+datetime.timedelta(days=90)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = [_x.date() for _x in x_dates],
            y = patient_data["meta"],
            mode="lines",
            name="Current",
            hovertemplate =
            '<br><b>Date</b>: %{x}<br>'+
            '<b>Margin</b>: %{y}'+
            '<extra></extra>',
            ))
    fig.add_traces([
        go.Scatter(
            x = [today, date_3m_later],
            y = [patient_data["meta"][-1], preditions[k]],
            mode="lines",
            name = k,
            text = [k,k],
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
    # fig.layout.plot_bgcolor = "#FFFFFF"
    # fig.layout.paper_bgcolor='rgba(0,0,0,0)'
    fig.layout.plot_bgcolor='rgba(0,0,0,0)'

    fig.update_layout(
        shapes=[
            dict(
                type= 'line',
                line=dict(
                    color = "Grey",
                    dash = "dash"),
                yref= 'paper', y0= 0, y1= 1,
                xref= 'x', x0= x_dates[-1], x1= x_dates[-1],
            ),
    ])
    fig.update_yaxes(
        tickprefix="$",rangemode="nonnegative", 
        linecolor="black",tickcolor="black", ticks='inside',)
    
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [x_dates[-1], date_3m_later],
            ticktext = [x_dates[-1].strftime("%b %Y"), date_3m_later.strftime("%b %Y")],
            range = [x_dates[0], date_3m_later + datetime.timedelta(days=14)], 
            linecolor = "black", tickcolor="black", ticks='inside',
            )
        )
    return fig