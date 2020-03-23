import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


trail_name = \
    st.sidebar.selectbox('Select Trail', os.listdir(os.path.join(os.getcwd(), 'experiments')))

csv_files = list(filter(lambda x: '.csv' in x, os.listdir(
    os.path.join(os.getcwd(), 'experiments', trail_name))))
csv_files.sort()

# load county data for the lat and long data
countys = pd.read_csv('Data/cleaned/counties.csv', 
    usecols=['State', 'County', 'Latitude', 'Longitude'])

f'# Simulated Spread of COVID-19 in US counties from {trail_name}'

date_display = st.empty()
date_idx = \
    st.slider('Select the number of day simulated', 0, len(csv_files)-1)
date_display.markdown(f'### Date: {csv_files[date_idx].split(".")[0]}')

'### Simulated spread'
df = pd.read_csv(
    os.path.join(os.getcwd(), 'experiments', trail_name, csv_files[date_idx]))

df = df[df.Infected != 0]
df = pd.merge(df, countys, how='left', on=['State', 'County'])

# create map
fig = go.Figure(data=go.Scattergeo(
        lon = df['Longitude'],
        lat = df['Latitude'],
        text = df['County'] + ', Infected: ' + df['Infected'].astype(str)\
            + ', Confirmed: ' + df['Confirmed'].astype(str)\
            + ', Death: ' + df['Death'].astype(str),
        mode = 'markers',
        marker_color = np.log(df['Infected'] / df['Population']),
    ))

fig.update_layout(
    title = 'Confirmed Cases over Population Size of US Counties',
    geo_scope='usa',
    )

fig   # display map
df.drop(columns=['Latitude', 'Longitude'], inplace=True)
df # display dataframe
