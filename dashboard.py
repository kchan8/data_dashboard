import streamlit as st
import streamlit.version
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
import numpy as np
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from streamlit_js_eval import streamlit_js_eval

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

def show_data_1():
  st.session_state.show_data_1 = True
def hide_data_1():
  st.session_state.show_data_1 = False

def process_df(site_name, df, end_date_str):
  df = df.sort_index()

  end_time_obj = datetime.strptime(end_date_str, "%m%d%Y").replace(hour=23, minute=0) - timedelta(days=1)
  start_time_obj = end_time_obj.replace(day=1) - relativedelta(months=2)
  start_time_obj = start_time_obj.replace(hour=0, minute=0, second=0, microsecond=0)

  full_range = pd.date_range(start=start_time_obj, end=end_time_obj, freq='h')
  # missing = full_range.difference(df.index)
  # st.write(missing)
  df_mod = df.reindex(full_range)

  col1, col2 = st.columns([1, 3])
  with col1:
    st.subheader(f"Streamlit version: {streamlit.__version__}")
  with col2:
    if st.button("Reset Date"):
      reset_date(df.index.min(), df.index.max())

  col1, col2, col3, col4, col5 = st.columns([7, 3, 1.5, 3, 4])
  with col1:
    st.title(f"{site_name} Dashboard From:")
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
    
  col1, col2, col3 = st.columns([1, 2, 6])
  with col1:
    show_outliers = st.checkbox("Show Outliers", value=True)
  with col2:
    if 'show_data_1' in st.session_state and st.session_state.show_data_1:
      st.button("Hide data point 1", on_click=hide_data_1)
    else:
      st.button("Add another data point", on_click=show_data_1)

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
  # show_outliers = st.checkbox("Show Outliers", value=True)
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

  if "show_data_1" not in st.session_state:
    st.session_state.show_data_1 = False
  # if not st.session_state.show_data_1:
  #   st.button("Add another data point", on_click=show_data_1)
  if st.session_state.show_data_1:
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    with col1:
      site_1 = st.selectbox("Site 1", list(sites.keys()))
    with col2:
      data_type_1 = st.selectbox("Data Type 1", get_keys(sites[site_1]))
    with col3:
      data_desc_1 = st.selectbox("Data Point 1", list(sites[site_1][data_type_1].keys()), key="1")
    with col4:
      match_1 = re.match(r"_(\d+)_(\d+)", sites[site_1][data_type_1][data_desc_1])
      if match_1:
        st.write(f"Entity ID: {int(match_1.group(1))}")
    data_point_1 = sites[site_1][data_type_1][data_desc_1]
    matches = re.findall(r'\d+', data_point_1)
    last_number = matches[-1] if matches else None
    match(last_number):
      case '1':
        unit_1 = 'kWh'
      case '2':
        unit_1 = 'thm'
      case '19':
        unit_1 = 'ccf'
      case '20':
        unit_1 = 'gal'
    if not show_outliers:
      # Use z-score or IQR method to filter out outliers
      q1_1 = df_mod[data_point_1].quantile(0.10)
      q3_1 = df_mod[data_point_1].quantile(0.90)
      iqr_1 = q3_1 - q1_1
      lower_bound_1 = q1_1 - 1.5 * iqr_1
      upper_bound_1 = q3_1 + 1.5 * iqr_1
      # df_plot = df_mod[(df_mod[data_point] >= lower_bound) & (df_mod[data_point] <= upper_bound)]
      df_plot_1 = df_mod.copy()
      mask = (df_plot_1[data_point_1] < lower_bound_1) | (df_plot_1[data_point_1] > upper_bound_1)
      df_plot_1.loc[mask, data_point_1] = np.nan
    else:
      df_plot_1 = df_mod

    with col4:
      if unit == unit_1:
        same_y_axis = st.checkbox("Use same y-axis", value=True)
      else:
        same_y_axis = False
      
  # this is low-level API that offers full customization and control
  start_dt = pd.to_datetime(start_date)
  end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
  time_range = (df_plot.index >= start_dt) & (df_plot.index <= end_dt)
  fig = go.Figure()

  fig.add_trace(go.Scatter(
    x=df_plot.index[time_range],
    y=df_plot[data_point][time_range],
    mode='lines',
    name='Hourly Data' if not st.session_state.show_data_1 else data_desc,
    yaxis='y1'
  ))
  
  if not st.session_state.show_data_1:
    df_daily = df_plot[data_point].resample('D').sum()
    date_range = (df_daily.index >= start_dt) & (df_daily.index <= end_dt)
    # shift display daily total at end of day
    df_daily.index = df_daily.index + pd.Timedelta(hours=23, minutes=59)
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
  else:
    fig.add_trace(go.Scatter(
      x=df_plot_1.index[time_range],
      y=df_plot_1[data_point_1][time_range],
      mode='lines',
      name=data_desc_1,
      line=dict(color='orange', width=2, dash='solid'),
      yaxis='y1' if same_y_axis else 'y2' 
    ))
    fig.update_layout(
      xaxis=dict(title="Date"),
      yaxis=dict(title=unit,
                  side='left',
                  showgrid=True),
      yaxis2=dict(title=unit_1,
                  overlaying='y',
                  side='right',
                  showgrid=False,
                  tickfont=dict(color='orange'),
                  titlefont=dict(color='orange')
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
  error_found = False
  for s in solar_check:
    if s["type"] == "Energy":
      solar_daily_data = df_mod[s["index"]].resample('D').sum()
      if solar_daily_data.iloc[-1] <= 10:
        if not error_found:
          error_found = True
          st.subheader(f"Check data point(s):")
        st.markdown(f"<div class='row-spacing'>{s['site']} / {s['name']}</div>", unsafe_allow_html=True)

  data_missing = list(df_mod[df_mod[data_point].isnull()].index)
  if data_missing:
    st.subheader(f"Time of missing data ({len(data_missing)})")
    cols_per_row = 7
    for i in range(0, len(data_missing), cols_per_row):
      cols = st.columns(cols_per_row)
      for j in range(cols_per_row):
        if i + j < len(data_missing):
          dt_obj = datetime.strptime(str(data_missing[i + j]), "%Y-%m-%d %H:%M:%S")
          # cols[j].write(dt_obj.strftime("%m/%d/%y %I:%M %p"))
          cols[j].markdown(
                    f"<div class='row-spacing'>{dt_obj.strftime('%m/%d/%y %I:%M %p')}</div>",
                    unsafe_allow_html=True
                )

# main program starts here
st.markdown("""
  <style>
    .block-container {
        padding-top: 1rem;
    }
    .row-spacing > div {
      margin-top: 0px !important;
      margin-bottom: 0px !important;
      padding-top: 0px !important;
      padding-bottom: 0px !important;
    }
  </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

screen_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIN_WIDTH')
# st.write("Width: ", screen_width)

if screen_width is not None and screen_width > 1130:
  col1, col2 = st.columns([1, 2])
else:
  col1, col2 = st.columns([1, 1])

with col1:
  siteInfo = st.file_uploader("Upload site info")
with col2:
  dataFile = st.file_uploader("Upload CSV Data file")

if siteInfo is not None:
  site_name = siteInfo.name.split('.')[0].capitalize()
  sites = pd.read_json(siteInfo)

if siteInfo is not None and dataFile is not None:
  match = re.search(r'_(\d{8})\.csv', dataFile.name)
  # skip 2nd line and the last line
  df = pd.read_csv(dataFile, skiprows=[1], header=0, skipfooter=1, index_col='time', parse_dates=['time'], engine='python')
  process_df(site_name, df, match.group(1))