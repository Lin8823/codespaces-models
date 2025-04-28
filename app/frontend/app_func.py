import requests
import traceback
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def draw_consumption_intake_chart():
    data = [
        {'day': 1, 'consumption': 120, 'intake': 200},
        {'day': 2, 'consumption': 70, 'intake': 400},
        {'day': 3, 'consumption': 93, 'intake': 100},
        {'day': 4, 'consumption': 153, 'intake': 253},
        {'day': 5, 'consumption': 88, 'intake': 198},
        {'day': 6, 'consumption': 97, 'intake': 211},
        {'day': 7, 'consumption': 200, 'intake': 137},
    ]

    df = pd.DataFrame(data)

    # draw the chart
    fig = go.Figure()

    # bar chart: daily consumption
    fig.add_trace(go.Bar(
        x=df['day'],
        y=df['consumption'],
        name='Consumption (hours)',
        marker_color='skyblue'
    ))

    # line chart: daily intake
    fig.add_trace(go.Scatter(
        x=df['day'],
        y=df['intake'],
        mode='lines+markers',
        name='Intake (calories)',
        line=dict(color='orange')
    ))

    # update layout
    fig.update_layout(
        title='Weekly Consumption and Intake Analysis',
        xaxis_title='Day of the Week',
        yaxis_title='Values',
        barmode='group',
        template='plotly_white'
    )

    st.plotly_chart(fig)

def draw_sleep_chart():
    data = [
        {'day': 1, 'time_in_bed': 6, 'bed_time': '21:00'},
        {'day': 2, 'time_in_bed': 7, 'bed_time': '23:00'},
        {'day': 3, 'time_in_bed': 3, 'bed_time': '00:00'},
        {'day': 4, 'time_in_bed': 5, 'bed_time': '21:00'},
        {'day': 5, 'time_in_bed': 8, 'bed_time': '22:00'},
        {'day': 6, 'time_in_bed': 9, 'bed_time': '22:00'},
        {'day': 7, 'time_in_bed': 2, 'bed_time': '22:00'},
    ]
    avg = 40 / 7  # average sleep
    recommendation = 50 / 7  # average recommendation

    df = pd.DataFrame(data)

    # draw the chart
    fig = go.Figure()

    # bar chart: time in bed
    fig.add_trace(go.Bar(
        x=df['day'],
        y=df['time_in_bed'],
        name='Time in Bed (hours)',
        marker_color='skyblue'
    ))

    # line chart: average sleep
    fig.add_trace(go.Scatter(
        x=df['day'],
        y=[avg] * len(df),
        mode='lines',
        name='Average Sleep',
        line=dict(color='orange', dash='dash')
    ))

    # line chart: recommended sleep
    fig.add_trace(go.Scatter(
        x=df['day'],
        y=[recommendation] * len(df),
        mode='lines',
        name='Recommended Sleep',
        line=dict(color='green', dash='dash')
    ))

    # update layout
    fig.update_layout(
        title='Weekly Sleep Analysis',
        xaxis_title='Day of the Week',
        yaxis_title='Time in Bed (hours)',
        barmode='group',
        template='plotly_white'
    )

    # display the chart
    st.plotly_chart(fig)