import streamlit as st
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def process_df(df):
  df = df.sort_index()
  full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='h')
  # missing = full_range.difference(df.index)
  # st.write(missing)
  df_mod = df.reindex(full_range)
  st.title(f"Oracle Dashboard {df.index.min().date()}  to {df.index.max().date()}")

  sites = {
    "Burlington": {
      "Energy": {
        "VDG 6": "_6000_1",
        "Energy Received From Grid": "_6050_1",
        "Energy Delivered to Grid (Solar Surplus)": "_6051_1",
        "Solar Generation": "_6052_1"
      },
      "Water": {
        "VDG 6": "_6000_20"
      }
    },
    "Austin": {
      "Energy" : {
        "Central Utility Plant": "_20050_1",
        "South Wing": "_30000_1",
        "Austin Waterfront": "_20000_1",
        "East Wing": "_26000_1",
        "Garage": "_20060_1",
        "West Wing": "_27000_1",
      },
      "Gas": {
        "East and West Wing Gas Meter": "_20044_2",
      },
      "Water": {
        "Central Utility Plant": "_20050_20",
        "South Domestic Water": "_20043_20",
        "East Domestic Water": "_20042_20",
        "West Domestic Water": "_20041_20",
      }
    },
    "Guadalajara": {
      "Energy": {
        "Utility": "_90020_1",
        "GDL06": "_90010_1",
        "Solar": "_90030_1"
      },
      "Gas": {
        "Cafe": "_90083_2",
        "Boiler": "_91109_2"
      },
      "Water": {
        "Cold Prep Rm": "_91100_19",
        "Garbage Rm": "_91101_19",
        "Storage Rm": "_91102_19",
        "Int Cuisine": "_91103_19",
        "Gen Cuisine": "_91105_19",
        "Solar Hot Water": "_91106_19"
      }
    },
    "Innovation Labs": {
      "Energy": {
        "Main Meter": "_110002_1",
        "Innovation Lab Ph2": "_110001_1",
        "EV": "_110023_1",
        "SmartStudioLoad Total": "_110020_1",
        "PV Total": "_110010_1",
      },
      "Gas": {
        "Innovation Lab Ph2": "_110001_2"
      },
      "Water": {
        "Innovation Lab Ph2 (ccf)": "_110001_19",
        "Innovation Lab Ph2 (gal)": "_110001_20",
      }
    },
    "Pleasanton": {
      "Energy": {
        "Pleasanton": "_70000_1",
        "Fuel Cell": "_72080_1",
        "Building 1": "_71000_1",
        "B1 Main": "_71010_1",
        "B1 Fuel Cell Allocation": "_71083_1",
        "B1 Solar": "_71020_1",
        "Building 2": "_72000_1",
        "B2 Main": "_72010_1",
        "B2 Fuel Cell Allocation": "_72093_1",
        "B2 Solar": "_72020_1",
      },
      "Gas": {
        "Fuel Cell": "_72080_2",
        "B1 Fuel Cell": "_71083_2",
        "B2 Cafe": "_72067_2",
        "B2 Fuel Cell": "_72093_2"
      },
      "Water": {
        "B1 Main": "_71010_19",
        "B2 Main": "_72010_19",
        "B2 Cafe": "_72067_19",
        "B1 CT Makeup": "_71081_19",
        "B2 CT Makeup": "_72091_19"
      }
    },
    "Redwood Shores": {
      "Energy": {
        "Redwood Shores": "_1_1",
        "Building 100": "_10_1",
        "Building 200": "_50_1",
        "Building 250": "_60_1",
        "Building 300": "_70_1",
        "Building 350": "_80_1",
        "Building 400": "_20_1",
        "Building 500": "_90_1",
        "Building 600": "_100_1",
        "Building 100 Office": "_14_1",
        "Building 200 Office": "_57_1",
        "Building 250 Office": "_66_1",
        "Building 300 Office": "_77_1",
        "Building 350 Office": "_87_1",
        "Building 400 Office": "_27_1",
        "Building 500 Office": "_97_1",
        "Building 600 Office": "_107_1",
        "Lab 103": "_12_1",
        "Lab 106": "_13_1",
        "Lab 400": "_22_1",
        "Lab 500": "_92_1",
        "Lab 600": "_102_1",
        "200 SWBD 1": "_53_1",
        "200 SWBD 2": "_54_1",
        "300 SWBD 1": "_73_1",
        "300 SWBD 2": "_74_1",
        "400 SWBD 1": "_23_1",
        "400 SWBD 2": "_24_1",
        "600 SWBD 1": "_103_1",
        "600 SWBD 2": "_104_1",
      },
      "Gas": {
        "Building 100": "_10_2",
        "Building 200": "_50_2",
        "Building 250": "_60_2",
        "Building 300": "_70_2",
        "Building 350": "_80_2",
        "Building 400": "_20_2",
        "Building 500": "_90_2",
        "Building 600": "_100_2",
        "250 G4": "_62_2",
        "250 G5":"_63_2",
      },
      "Water": {
        "Building 100": "_10_19",
        "Building 200": "_50_19",
        "Building 250": "_60_19",
        "Building 300": "_70_19",
        "Building 350": "_80_19",
        "Building 400": "_20_19",
        "Building 500": "_90_19",
        "Building 600": "_100_19",
      }
    },
    "Santa Clara": {
      "Energy": {
        "SCA03": "_40300_1",
        "SCA04": "_40400_1",
        "SCA05": "_40500_1",
        "SCA06": "_40600_1",
        "SCA07": "_40700_1",
        "SCA09": "_9000_1",
        "SCA10": "_10000_1",
        "SCA11": "_41100_1",
        "SCA12": "_41200_1",
        "SCA14": "_41400_1",
        "SCA15": "_41500_1",
        "SCA16": "_41600_1",
        "SCA17": "_41700_1",
        "SCA18": "_41800_1",
        "SCA19": "_41900_1",
        "SCA20": "_42000_1",
        "SCA21": "_42100_1",
        "SCA22": "_42200_1",
        "SCA23": "_42300_1",
        "SCA05 IT": "_40520_1",
        "SCA09 IT": "_9154_1",
        "SCA10 IT": "_10004_1",
        "SCA11 IT": "_41120_1",
        "SCA12 IT": "_41220_1",
        "SCA15 IT": "_41520_1",
        "SCA16 IT": "_41620_1",
        "SCA17 IT": "_41720_1",
        "SCA18 IT": "_41820_1",
        "SCA19 IT": "_41920_1",
        "SCA20 IT": "_42020_1",
        "SCA21 IT": "_42120_1",
        "SCA22 IT": "_42220_1",
        "Santa Clara": "_4_1",
      },
      "Gas": {
        "SCA03": "_40300_2",
        "SCA04": "_40400_2",
        "SCA05": "_40500_2",
        "SCA06": "_40600_2",
        "SCA07": "_40700_2",
        "SCA09": "_9000_2",
        "SCA10": "_10000_2",
        "SCA11": "_41100_2",
        "SCA12": "_41200_2",
        "SCA14": "_41400_2",
        "SCA15": "_41500_2",
        "SCA16": "_41600_2",
        "SCA17": "_41700_2",
        "SCA18": "_41800_2",
        "SCA19": "_41900_2",
        "SCA20": "_42000_2",
        "SCA21": "_42100_2",
        "SCA22": "_42200_2",
        "SCA23": "_42300_2",
        "SCA23 Fitness": "_42310_2",
        "SCA23 Kitchen": "_42320_2",
        "SCA23 Other": "_42330_2",
      },
      "Water": {
        "SCA03": "_40300_19",
        "SCA04": "_40400_19",
        "SCA05": "_40500_19",
        "SCA06": "_40600_19",
        "SCA07": "_40700_19",
        "SCA09": "_9000_19",
        "SCA10": "_10000_19",
        "SCA11": "_41100_19",
        "SCA12": "_41200_19",
        "SCA14": "_41400_19",
        "SCA15": "_41500_19",
        "SCA16": "_41600_19",
        "SCA17": "_41700_19",
        "SCA18": "_41800_19",
        "SCA19": "_41900_19",
        "SCA20": "_42000_19",
        "SCA21": "_42100_19",
        "SCA22": "_42200_19",
        "SCA23": "_42300_19",
        "SCA09 Recovered Water": "_9002_19",
        "SCA10 Recovered Water": "_10007_19",
      }
    }
  }

  col1, col2, col3 = st.columns([1, 1, 2])
  with col1:
    site = st.selectbox("Site", list(sites.keys()))
  with col2:
    data_type = st.selectbox("Data Type", list(sites[site].keys()))
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
    q1 = df_mod[data_point].quantile(0.25)
    q3 = df_mod[data_point].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    df_plot = df_mod[(df_mod[data_point] >= lower_bound) & (df_mod[data_point] <= upper_bound)]
  else:
    df_plot = df_mod

  fig = px.line(df_plot, x=df_plot.index, y=data_point)
  fig.update_layout(xaxis_title="Date", yaxis_title=unit)
  st.plotly_chart(fig, use_container_width=True)

# main program starts here
st.markdown("""
  <style>
      .block-container {
          padding-top: 1rem;
      }
  </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

dataFile = st.file_uploader("Upload CSV Data file")

if dataFile is not None:
  # skip 2nd line and the last line
  df = pd.read_csv(dataFile, skiprows=[1], header=0, skipfooter=1, index_col='time', parse_dates=['time'], engine='python')
  process_df(df)