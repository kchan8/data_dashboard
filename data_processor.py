"""
Main data processing logic for the dashboard.
"""
import streamlit as st
import pandas as pd
from utils import (
    prepare_dataframe, filter_outliers, get_missing_data_timestamps,
    check_solar_data_issues
)
from plotting import create_single_data_chart, create_comparison_chart
from ui_components import (
    create_header_section, create_date_selection_section, create_control_section,
    create_data_selection_section,
    display_solar_issues, display_missing_data
)


class DashboardProcessor:
    """Main processor class for the energy dashboard."""
    
    def __init__(self, site_name, df, end_date_str, sites, streamlit_version):
        """
        Initialize the dashboard processor.
        
        Args:
            site_name: Name of the site
            df: Input dataframe
            end_date_str: End date string
            sites: Sites configuration dictionary
            streamlit_version: Streamlit version string
        """
        self.site_name = site_name
        self.df_original = df
        self.end_date_str = end_date_str
        self.sites = sites
        self.streamlit_version = streamlit_version
        self.df_processed = None
        
        # Initialize session state
        if "show_data_1" not in st.session_state:
            st.session_state.show_data_1 = False
    
    def prepare_data(self):
        """Prepare the dataframe with proper time range."""
        self.df_processed = prepare_dataframe(self.df_original, self.end_date_str)
    
    def create_ui_components(self):
        """Create all UI components and get user inputs."""
        # Header section
        create_header_section(self.site_name, self.df_processed, self.streamlit_version)
        
        # Date selection
        start_date, end_date = create_date_selection_section(self.site_name, self.df_processed)
        
        # Control section
        show_outliers = create_control_section()
        
        # Primary data selection
        site, data_type, data_desc, data_point, unit, same_y_axis = create_data_selection_section(self.sites)
        
        # Secondary data selection (if enabled)
        secondary_data = None
        # same_y_axis = False
        
        if st.session_state.show_data_1:
            site_1, data_type_1, data_desc_1, data_point_1, unit_1, same_y_axis = create_data_selection_section(
                self.sites, "1", True, unit
            )
            
            secondary_data = {
                'site': site_1,
                'data_type': data_type_1,
                'data_desc': data_desc_1,
                'data_point': data_point_1,
                'unit': unit_1
            }
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'show_outliers': show_outliers,
            'primary_data': {
                'site': site,
                'data_type': data_type,
                'data_desc': data_desc,
                'data_point': data_point,
                'unit': unit
            },
            'secondary_data': secondary_data,
            'same_y_axis': same_y_axis
        }
    
    def process_and_display(self, config):
        """
        Process data and display charts based on configuration.
        
        Args:
            config: Configuration dictionary from UI components
        """
        # Extract configuration
        start_date = config['start_date']
        end_date = config['end_date']
        show_outliers = config['show_outliers']
        primary_data = config['primary_data']
        secondary_data = config['secondary_data']
        same_y_axis = config['same_y_axis']
        
        # Convert dates to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
        
        # Filter primary data
        df_plot = filter_outliers(self.df_processed, primary_data['data_point'], show_outliers)
        
        # Create chart based on whether we have secondary data
        if secondary_data is None:
            # Single data point chart
            fig = create_single_data_chart(
                df_plot, primary_data['data_point'], primary_data['unit'], start_dt, end_dt
            )
        else:
            # Comparison chart
            df_plot_1 = filter_outliers(self.df_processed, secondary_data['data_point'], show_outliers)
            fig = create_comparison_chart(
                df_plot, primary_data['data_point'], primary_data['unit'], primary_data['data_desc'],
                df_plot_1, secondary_data['data_point'], secondary_data['unit'], secondary_data['data_desc'],
                start_dt, end_dt, same_y_axis
            )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Check for solar data issues
        problematic_points = check_solar_data_issues(self.sites.to_dict(), self.df_processed)
        display_solar_issues(problematic_points)
        
        # Display missing data information
        missing_data = get_missing_data_timestamps(self.df_processed, primary_data['data_point'])
        display_missing_data(missing_data)
    
    def run(self):
        """Main execution method."""
        self.prepare_data()
        config = self.create_ui_components()
        self.process_and_display(config)


def process_df(site_name, df, end_date_str, sites, streamlit_version):
    """
    Main processing function - refactored for better organization.
    
    Args:
        site_name: Name of the site
        df: Input dataframe
        end_date_str: End date string
        sites: Sites configuration
        streamlit_version: Streamlit version string
    """
    processor = DashboardProcessor(site_name, df, end_date_str, sites, streamlit_version)
    processor.run()