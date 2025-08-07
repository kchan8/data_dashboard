"""
Streamlit UI components and display functions.
"""
import streamlit as st
from datetime import datetime
from utils import get_keys, get_entity_id, get_unit_from_data_point


def setup_page_config():
    """Set up Streamlit page configuration and custom CSS."""
    st.set_page_config(layout="wide")
    
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


def create_file_upload_section(screen_width):
    """
    Create file upload section with responsive layout.
    
    Args:
        screen_width: Screen width for responsive design
        
    Returns:
        Tuple of (site_info_file, data_file)
    """
    if screen_width is not None and screen_width > 1130:
        col1, col2 = st.columns([1, 2])
    else:
        col1, col2 = st.columns([1, 1])

    with col1:
        site_info = st.file_uploader("Upload site info")
    with col2:
        data_file = st.file_uploader("Upload CSV data file")
    
    return site_info, data_file


def create_header_section(site_name, df, streamlit_version):
    """
    Create header section with title and reset button.
    
    Args:
        site_name: Name of the site
        df: Dataframe for min/max dates
        streamlit_version: Streamlit version string
    """
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader(f"Streamlit version: {streamlit_version}")
    with col2:
        if st.button("Reset Date"):
            reset_date(df.index.min(), df.index.max())


def create_date_selection_section(site_name, df):
    """
    Create date selection section.
    
    Args:
        site_name: Name of the site
        df: Dataframe for date range limits
        
    Returns:
        Tuple of (start_date, end_date)
    """
    col1, col2, col3, col4, col5 = st.columns([7, 3, 1.5, 3, 4])
    
    with col1:
        st.title(f"{site_name} Dashboard From:")
    
    with col2:
        if 'start_date' not in st.session_state:
            st.session_state.start_date = df.index.min()
        start_date = st.date_input(
            ' ',
            min_value=df.index.min(),
            max_value=df.index.max(),
            key='start_date'
        )
    
    with col3:
        st.title("To:")
    
    with col4:
        if 'end_date' not in st.session_state:
            st.session_state.end_date = df.index.max()
        end_date = st.date_input(
            ' ',
            min_value=df.index.min(),
            max_value=df.index.max(),
            key='end_date'
        )
    
    return start_date, end_date


def create_control_section():
    """
    Create control section with outliers checkbox and data point toggle.
    
    Returns:
        Boolean for show_outliers
    """
    col1, col2, col3 = st.columns([1, 2, 6])
    
    with col1:
        show_outliers = st.checkbox("Show Outliers", value=True)
    
    with col2:
        if 'show_data_1' in st.session_state and st.session_state.show_data_1:
            st.button("Hide data point 1", on_click=hide_data_1)
        else:
            st.button("Add another data point", on_click=show_data_1)
    
    return show_outliers


def create_data_selection_section(sites, key_suffix="", show_same_y_axis_option=False, ref_unit=""):
    """
    Create data selection dropdowns.
    
    Args:
        sites: Sites dictionary
        key_suffix: Suffix for unique keys
        
    Returns:
        Tuple of (site, data_type, data_desc, data_point, unit)
    """
    # Unique key for session state
    site_key = f"site{key_suffix}"
    prev_site_key = f"prev_site{key_suffix}"
    type_key = f"data_type{key_suffix}"
    prev_type_key = f"prev_type{key_suffix}"
    index_key = f"data_index{key_suffix}"
    if prev_site_key not in st.session_state:
        st.session_state[prev_site_key] = None
    if type_key not in st.session_state:
        st.session_state[type_key] = "Energy"
    if prev_type_key not in st.session_state:
        st.session_state[prev_type_key] = None
    if index_key not in st.session_state:
        st.session_state[index_key] = 0

    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 0.3, 1])
    
    with col1:
        site = st.selectbox(f"Site{' ' + key_suffix if key_suffix else ''}", 
                           list(sites.keys()), 
                           key=site_key)
        if st.session_state[prev_site_key] != site:
            st.session_state[index_key] = 0
            st.session_state[prev_site_key] = site
            st.session_state[type_key] = "Energy"
        
    with col2:
        data_type = st.selectbox(f"Data Type{' ' + key_suffix if key_suffix else ''}", 
                               get_keys(sites[site]), 
                               key=type_key)
        if st.session_state[prev_type_key] != data_type:
            st.session_state[index_key] = 0
            st.session_state[prev_type_key] = data_type
    with col3:
        data_keys = list(sites[site][data_type].keys())
        data_key_count = len(data_keys)
        data_desc = st.selectbox(f"Data Point{' ' + key_suffix if key_suffix else ''}", 
                               data_keys,
                               index=st.session_state[index_key],
                               key=f"data_desc{key_suffix}")
        if data_desc != data_keys[st.session_state[index_key]]:
            st.session_state[index_key] = data_keys.index(data_desc)

    with col4:    
        if st.button("Prev", key=f"prev{key_suffix}"):
            st.session_state[index_key] = (st.session_state[index_key] - 1) % data_key_count
            st.rerun()
        if st.button("Next", key=f"next{key_suffix}"):
            st.session_state[index_key] = (st.session_state[index_key] + 1) % data_key_count
            st.rerun()

    with col5:
        data_point = sites[site][data_type][data_desc]
        entity_id = get_entity_id(data_point)
        if entity_id:
            st.write(f"Entity ID: {entity_id}")
        unit = get_unit_from_data_point(data_point)
        if show_same_y_axis_option and ref_unit == unit:
            same_y_axis = st.checkbox("Use same y-axis", value=True)
        else:
            same_y_axis = False
    
    return site, data_type, data_desc, data_point, unit, same_y_axis


def display_solar_issues(problematic_points):
    """
    Display solar data issues.
    
    Args:
        problematic_points: List of problematic solar data points
    """
    if problematic_points:
        st.subheader("Check data point(s):")
        for point in problematic_points:
            st.markdown(
                f"<div class='row-spacing'>{point['site']} / {point['name']}</div>",
                unsafe_allow_html=True
            )


def display_missing_data(missing_data):
    """
    Display missing data timestamps in a grid layout.
    
    Args:
        missing_data: List of missing data timestamps
    """
    if missing_data:
        st.subheader(f"Time of missing data ({len(missing_data)})")
        cols_per_row = 7
        
        for i in range(0, len(missing_data), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(missing_data):
                    dt_obj = datetime.strptime(str(missing_data[i + j]), "%Y-%m-%d %H:%M:%S")
                    cols[j].markdown(
                        f"<div class='row-spacing'>{dt_obj.strftime('%m/%d/%y %I:%M %p')}</div>",
                        unsafe_allow_html=True
                    )


# Session state management functions
def reset_date(start_date, end_date):
    """Reset date range in session state."""
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date
    st.rerun()


def show_data_1():
    """Enable second data point display."""
    st.session_state.show_data_1 = True


def hide_data_1():
    """Disable second data point display."""
    st.session_state.show_data_1 = False