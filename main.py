"""
Main Streamlit application entry point.
"""
import streamlit as st
import pandas as pd
import re
from streamlit_js_eval import streamlit_js_eval

from ui_components import setup_page_config, create_file_upload_section
from data_processor import process_df


def main():
    """Main application function."""
    # Set up page configuration
    setup_page_config()
    
    # Get screen width for responsive layout
    screen_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIN_WIDTH')
    
    # Create file upload section
    site_info, data_file = create_file_upload_section(screen_width)
    
    # Process uploaded files
    if site_info is not None:
        site_name = site_info.name.split('.')[0].capitalize()
        sites = pd.read_json(site_info)
    
    if site_info is not None and data_file is not None:
        try:
            # Extract date from filename
            match = re.search(r'_(\d{8})(?:_[^_]*)?\.csv', data_file.name)
            if not match:
                st.error("Could not extract date from filename. Expected format: *_MMDDYYYY.csv")
                return
            
            # Read CSV file
            df = pd.read_csv(
                data_file,
                skiprows=[1],
                header=0,
                skipfooter=1,
                index_col='time',
                parse_dates=['time'],
                engine='python'
            )
            
            # Process and display dashboard
            process_df(site_name, df, match.group(1), sites, st.__version__)
            
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.error("Please check that your files are in the correct format.")


if __name__ == "__main__":
    main()