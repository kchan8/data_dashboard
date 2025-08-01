"""
Chart generation and plotting functions using Plotly.
"""
import pandas as pd
import plotly.graph_objects as go


def create_single_data_chart(df_plot, data_point, unit, start_dt, end_dt):
    """
    Create a chart with single data point showing hourly, daily, and EMA data.
    
    Args:
        df_plot: Filtered dataframe
        data_point: Column name for the data
        unit: Unit string for labels
        start_dt: Start datetime
        end_dt: End datetime
        
    Returns:
        Plotly figure object
    """
    time_range = (df_plot.index >= start_dt) & (df_plot.index <= end_dt)
    fig = go.Figure()
    
    # Add hourly data trace
    fig.add_trace(go.Scatter(
        x=df_plot.index[time_range],
        y=df_plot[data_point][time_range],
        mode='lines',
        name='Hourly Data',
        yaxis='y1'
    ))
    
    # Add daily total trace
    df_daily = df_plot[data_point].resample('D').sum()
    date_range = (df_daily.index >= start_dt) & (df_daily.index <= end_dt)
    # Shift display daily total to end of day
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
    
    # Add 7-day EMA trace
    df_ema = df_daily.ewm(span=7, adjust=False).mean()
    fig.add_trace(go.Scatter(
        x=df_ema.index[date_range],
        y=df_ema.values[date_range],
        mode='lines',
        name='7-Day EMA',
        line=dict(color='green', width=2, dash='solid'),
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(
            title=f"Hourly {unit}",
            side='left',
            showgrid=True
        ),
        yaxis2=dict(
            title=f"Daily Total {unit}",
            overlaying='y',
            side='right',
            showgrid=False,
            tickfont=dict(color='red'),
            titlefont=dict(color='red')
        ),
        legend=dict(
            x=1.1,
            y=1,
            xanchor='left',
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='gray',
            borderwidth=1
        )
    )
    
    return fig


def create_comparison_chart(df_plot, data_point, unit, data_desc,
                           df_plot_1, data_point_1, unit_1, data_desc_1,
                           start_dt, end_dt, same_y_axis=False):
    """
    Create a chart comparing two data points.
    
    Args:
        df_plot: First dataframe
        data_point: First data column
        unit: First data unit
        data_desc: First data description
        df_plot_1: Second dataframe
        data_point_1: Second data column
        unit_1: Second data unit
        data_desc_1: Second data description
        start_dt: Start datetime
        end_dt: End datetime
        same_y_axis: Whether to use same y-axis for both datasets
        
    Returns:
        Plotly figure object
    """
    time_range = (df_plot.index >= start_dt) & (df_plot.index <= end_dt)
    fig = go.Figure()
    
    # Add first data trace
    fig.add_trace(go.Scatter(
        x=df_plot.index[time_range],
        y=df_plot[data_point][time_range],
        mode='lines',
        name=data_desc,
        yaxis='y1'
    ))
    
    # Add second data trace
    fig.add_trace(go.Scatter(
        x=df_plot_1.index[time_range],
        y=df_plot_1[data_point_1][time_range],
        mode='lines',
        name=data_desc_1,
        line=dict(color='orange', width=2, dash='solid'),
        yaxis='y1' if same_y_axis else 'y2'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(
            title=unit,
            side='left',
            showgrid=True
        ),
        yaxis2=dict(
            title=unit_1,
            overlaying='y',
            side='right',
            showgrid=False,
            tickfont=dict(color='orange'),
            titlefont=dict(color='orange')
        ),
        legend=dict(
            x=1.1,
            y=1,
            xanchor='left',
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='gray',
            borderwidth=1
        )
    )
    
    return fig