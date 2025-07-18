import streamlit as st
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
import numpy as np
from datetime import datetime

def get_keys(obj):
  keys = []
  for k, v in obj.items():
    if v is not None and not (isinstance(v, float) and math.isnan(v)):
      keys.append(k)      
  return keys

def process_df(df):
  df = df.sort_index()
  full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='h')
  # missing = full_range.difference(df.index)
  # st.write(missing)
  df_mod = df.reindex(full_range)
  st.title(f"Dashboard {df.index.min().date()}  to {df.index.max().date()}")

  col1, col2, col3 = st.columns([1, 1, 2])
  with col1:
    site = st.selectbox("Site", list(sites.keys()))
  with col2:
    data_type = st.selectbox("Data Type", get_keys(sites[site]))
  with col3:
    data_desc = st.selectbox("Data Point", list(sites[site][data_type].keys()))
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

  fig = px.line(df_plot, x=df_plot.index, y=data_point)
  fig.update_layout(xaxis_title="Date", yaxis_title=unit)
  st.plotly_chart(fig, use_container_width=True)

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

if dataFile is not None:
  # skip 2nd line and the last line
  df = pd.read_csv(dataFile, skiprows=[1], header=0, skipfooter=1, index_col='time', parse_dates=['time'], engine='python')
  process_df(df)