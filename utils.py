"""
Utility functions for data processing and helper operations.
"""
import re
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

def get_keys(obj):
    """Extract non-null keys from a dictionary object."""
    keys = []
    for k, v in obj.items():
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            keys.append(k)
    return keys


def find_data_points(d, search_str):
    """
    Recursively search for data points containing a specific string.
    
    Args:
        d: Dictionary/object to search through
        search_str: String to search for in keys
        
    Returns:
        List of dictionaries containing site, type, name, and index information
    """
    data_points = []
    
    def traverse(obj, path=[]):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = path + [k]
                if search_str in k.lower():
                    data_points.append({
                        "site": path[0] if path else None,
                        "type": path[1] if len(path) > 1 else None,
                        "name": k,
                        "index": v
                    })
                traverse(v, new_path)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item, path)
    
    traverse(d)
    return data_points


def get_unit_from_data_point(data_point):
    """
    Extract unit type from data point string based on last number.
    
    Args:
        data_point: String containing data point identifier
        
    Returns:
        String representing the unit type
    """
    matches = re.findall(r'\d+', data_point)
    last_number = matches[-1] if matches else None
    
    unit_mapping = {
        '1': 'kWh',
        '2': 'thm',
        '19': 'ccf',
        '20': 'gal'
    }
    
    return unit_mapping.get(last_number, 'Unknown')


def get_entity_id(data_point):
    """
    Extract entity ID from data point string.
    
    Args:
        data_point: String containing data point identifier
        
    Returns:
        Integer entity ID or None if not found
    """
    match = re.match(r"_(\d+)_(\d+)", data_point)
    return int(match.group(1)) if match else None

def is_last_day_of_month(dt: datetime) -> bool:
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return dt.day == last_day

def prepare_dataframe(df, end_date_str):
    """
    Prepare dataframe with proper time range and missing data handling.
    
    Args:
        df: Input dataframe with datetime index
        end_date_str: End date string in format MMDDYYYY
        
    Returns:
        Reindexed dataframe with full time range
    """
    df = df.sort_index()
    
    end_time_obj = datetime.strptime(end_date_str, "%m%d%Y").replace(hour=23, minute=0) - timedelta(days=1)
    if is_last_day_of_month(end_time_obj):
        start_time_obj = end_time_obj.replace(day=1) - relativedelta(months=1)
    else:
        start_time_obj = end_time_obj.replace(day=1) - relativedelta(months=2)
    start_time_obj = start_time_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    
    full_range = pd.date_range(start=start_time_obj, end=end_time_obj, freq='h')
    df_reindexed = df.reindex(full_range)
    
    return df_reindexed


def filter_outliers(df, data_point, show_outliers=True):
    """
    Filter outliers from dataframe using IQR method.
    
    Args:
        df: Input dataframe
        data_point: Column name to filter
        show_outliers: Boolean to show/hide outliers
        
    Returns:
        Filtered dataframe
    """
    if show_outliers:
        return df
    
    df_filtered = df.copy()
    q1 = df[data_point].quantile(0.10)
    q3 = df[data_point].quantile(0.90)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    mask = (df_filtered[data_point] < lower_bound) | (df_filtered[data_point] > upper_bound)
    df_filtered.loc[mask, data_point] = np.nan
    
    return df_filtered


def get_missing_data_timestamps(df, data_point):
    """
    Get list of timestamps where data is missing.
    
    Args:
        df: Input dataframe
        data_point: Column name to check
        
    Returns:
        List of datetime objects where data is missing
    """
    return list(df[df[data_point].isnull()].index)


def check_solar_data_issues(sites_dict, df):
    """
    Check for solar data points with very low daily totals.
    
    Args:
        sites_dict: Dictionary containing site information
        df: Dataframe with energy data
        
    Returns:
        List of problematic solar data points
    """
    solar_check = find_data_points(sites_dict, "solar")
    problematic_points = []
    
    for s in solar_check:
        if s["type"] == "Energy" and s["index"] in df.columns:
            solar_daily_data = df[s["index"]].resample('D').sum()
            if len(solar_daily_data) > 0 and solar_daily_data.iloc[-1] <= 10:
                problematic_points.append(s)
    
    return problematic_points