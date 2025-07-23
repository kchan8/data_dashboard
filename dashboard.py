import streamlit as st
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
import numpy as np
from datetime import date, datetime

def get_keys(obj):
  keys = []
  for k, v in obj.items():
    if v is not None and not (isinstance(v, float) and math.isnan(v)):
      keys.append(k)      
  return keys

def find_data_points(d, str):
    data_points = []
    def traverse(obj, path=[]):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = path + [k]
                if str in k.lower():
                    data_points.append({"site": path[0] if path else None, "type": path[1] if path else None, "name": k, "index": v})
                traverse(v, new_path)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item, path)
    traverse(d)
    return data_points

def reset_date(start_date, end_date):
  st.session_state.start_date = start_date
  st.session_state.end_date = end_date
  st.rerun()

def process_df(df):
  df = df.sort_index()
  full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='h')
  # missing = full_range.difference(df.index)
  # st.write(missing)
  df_mod = df.reindex(full_range)

  if st.button("Reset Date"):
    reset_date(df.index.min(), df.index.max())

  col1, col2, col3, col4, col5 = st.columns([5, 3, 1.5, 3, 3])
  with col1:
    st.title("Dashboard From:")
  with col2:
    if 'start_date' not in st.session_state:
      st.session_state.start_date = df.index.min()
    start_date = st.date_input(' ',
                               min_value=df.index.min(), 
                               max_value=df.index.max(), 
                               key='start_date')
  with col3:
    st.title("To:")
  with col4:
    if 'end_date' not in st.session_state:
      st.session_state.end_date = df.index.max()
    end_date = st.date_input(' ',
                             min_value=df.index.min(),
                             max_value=df.index.max(),
                             key='end_date')
  with col5:
    st.title(" ")

  col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
  with col1:
    site = st.selectbox("Site", list(sites.keys()))
  with col2:
    data_type = st.selectbox("Data Type", get_keys(sites[site]))
  with col3:
    data_desc = st.selectbox("Data Point", list(sites[site][data_type].keys()))
  with col4:
    match = re.match(r"_(\d+)_(\d+)", sites[site][data_type][data_desc])
    if match:
      st.write(f"Entity ID: {int(match.group(1))}")
  data_point = sites[site][data_type][data_desc]

  matches = re.findall(r'\d+', data_point)
  last_number = matches[-1] if matches else None
  match(last_number):
    case '1':
      unit = 'kWh'
    case '2':
      unit = 'thm'
    case '19':
      unit = 'ccf'
    case '20':
      unit = 'gal'

  # Checkbox to show/hide outliers
  show_outliers = st.checkbox("Show Outliers", value=True)
  if not show_outliers:
    # Use z-score or IQR method to filter out outliers
    q1 = df_mod[data_point].quantile(0.10)
    q3 = df_mod[data_point].quantile(0.90)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    # df_plot = df_mod[(df_mod[data_point] >= lower_bound) & (df_mod[data_point] <= upper_bound)]
    df_plot = df_mod.copy()
    mask = (df_plot[data_point] < lower_bound) | (df_plot[data_point] > upper_bound)
    df_plot.loc[mask, data_point] = np.nan
  else:
    df_plot = df_mod

  # this is hight-level API for quick and consise plotting
  # fig = px.line(df_plot, x=df_plot.index, y=data_point)
  # fig.update_layout(xaxis_title="Date", yaxis_title=unit)

  # this is low-level API that offers full customization and control
  start_dt = pd.to_datetime(start_date)
  end_dt = pd.to_datetime(end_date)
  time_range = (df_plot.index >= start_dt) & (df_plot.index <= end_dt)
  fig = go.Figure()
  fig.add_trace(go.Scatter(
    x=df_plot.index[time_range],
    y=df_plot[data_point][time_range],
    mode='lines',
    name='Hourly Data',
    yaxis='y1'
  ))
  
  df_daily = df_plot[data_point].resample('D').sum()
  # shift display daily total at end of day
  df_daily.index = df_daily.index + pd.Timedelta(hours=23, minutes=59)
  date_range = (df_daily.index >= start_dt) & (df_daily.index <= end_dt)
  # Add the daily total as a red line
  fig.add_trace(go.Scatter(
    x=df_daily.index[date_range],
    y=df_daily.values[date_range],
    mode='lines+markers',
    name='Daily Total',
    line=dict(color='red', width=2, dash='dot'),
    marker=dict(color='red'),
    yaxis='y2'
  ))

  df_ema = df_daily.ewm(span=7, adjust=False).mean()
  fig.add_trace(go.Scatter(
    x=df_ema.index[date_range],
    y=df_ema.values[date_range],
    mode='lines',
    name='7-Day EMA',
    line=dict(color='green', width=2, dash='solid'),
    yaxis='y2'  # solid green line
  ))

  # Update layout and display
  fig.update_layout(
    xaxis=dict(title="Date"),
    yaxis=dict(title="Hourly " + unit,
                side='left',
                showgrid=True),
    yaxis2=dict(title="Daily Total " + unit,
                overlaying='y',
                side='right',
                showgrid=False,
                tickfont=dict(color='red'),     # Make tick labels red
                titlefont=dict(color='red')     # Optional: make the axis title red too)
    ),
    # legend=dict(title="Legend")
    legend=dict(
      x=1.1,              # Move further to the right (default is 1)
      y=1,                # Top of the chart
      xanchor='left',     # Anchor the legend box to the left side of the x position
      bgcolor='rgba(255,255,255,0.5)',  # Optional: semi-transparent background
      bordercolor='gray',
      borderwidth=1
    )
  )

  st.plotly_chart(fig, use_container_width=True)

  # check all data points for solar that has very low daily total on previous day
  solar_check = find_data_points(sites.to_dict(), "solar")
  for s in solar_check:
    if s["type"] == "Energy":
      solar_daily_data = df_mod[s["index"]].resample('D').sum()
      if solar_daily_data.iloc[-1] <= 10:
        st.write(f"Note: Check site {s['site']} data point {s['name']}")

  data_missing = list(df_mod[df_mod[data_point].isnull()].index)
  if data_missing:
    st.header(f"Time of missing data ({len(data_missing)})")
    cols_per_row = 7
    for i in range(0, len(data_missing), cols_per_row):
      cols = st.columns(cols_per_row)
      for j in range(cols_per_row):
        if i + j < len(data_missing):
          dt_obj = datetime.strptime(str(data_missing[i + j]), "%Y-%m-%d %H:%M:%S")
          cols[j].write(dt_obj.strftime("%m/%d/%y %I:%M %p"))

# main program starts here
st.markdown("""
  <style>
      .block-container {
          padding-top: 1rem;
      }
  </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

col1, col2 = st.columns([1, 2])
with col1:
  siteInfo = st.file_uploader("Upload site info")
with col2:
  dataFile = st.file_uploader("Upload CSV Data file")

if siteInfo is not None:
  sites = pd.read_json(siteInfo)

if siteInfo is not None and dataFile is not None:
  # skip 2nd line and the last line
  df = pd.read_csv(dataFile, skiprows=[1], header=0, skipfooter=1, index_col='time', parse_dates=['time'], engine='python')
  process_df(df)