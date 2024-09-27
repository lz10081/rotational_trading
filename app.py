import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import datetime, date

# Set Streamlit page configuration
st.set_page_config(
    page_title="Rotational Trading System Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title of the Dashboard
st.title("📈 Rotational Trading System Backtest Dashboard")

# Function to load data with caching to improve performance
@st.cache_data
def load_data():
    """
    Loads the backtest results from CSV files.

    Returns:
        portfolio_df (pd.DataFrame): Daily portfolio values.
        trade_df (pd.DataFrame): Log of all trades.
        summary_df (pd.DataFrame): Summary of key performance metrics.
    """
    portfolio_df = pd.read_csv('portfolio_history.csv', parse_dates=['Date'])
    trade_df = pd.read_csv('trade_log.csv', parse_dates=['Date'])
    summary_df = pd.read_csv('summary.csv')
    return portfolio_df, trade_df, summary_df

# Load the data
portfolio_df, trade_df, summary_df = load_data()

# Sidebar for navigation (optional)
st.sidebar.header("Navigation")
sections = ["Performance Summary", "Portfolio vs SPY", "Daily Portfolio Value", "Trade Log", "Filter Trades by Stock"]
selected_section = st.sidebar.radio("Go to", sections)

# ----------- Performance Summary -----------
if selected_section == "Performance Summary":
    st.header("📊 Performance Summary")
    summary_display = summary_df.set_index('Metric')
    st.table(summary_display)

# ----------- Portfolio vs SPY Performance -----------
elif selected_section == "Portfolio vs SPY":
    st.header("📈 Portfolio vs SPY Performance")
    
    # Create Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_df['Date'],
        y=portfolio_df['Portfolio Return'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=portfolio_df['Date'],
        y=portfolio_df['SPY Return'],
        mode='lines',
        name='SPY Value',
        line=dict(color='orange')
    ))
    fig.update_layout(
        title='Portfolio vs SPY Performance Over Time',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------- Daily Portfolio Value -----------
elif selected_section == "Daily Portfolio Value":
    st.header("📈 Daily Portfolio Value Over Time")
    
    # Create Plotly figure
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=portfolio_df['Date'],
        y=portfolio_df['Portfolio Value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='green')
    ))
    fig2.update_layout(
        title='Daily Portfolio Value Over Time',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig2, use_container_width=True)

# ----------- Trade Log -----------
elif selected_section == "Trade Log":
    st.header("📋 Trade Log")
    
    # Configure AgGrid Options
    gb = GridOptionsBuilder.from_dataframe(trade_df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(editable=False, sortable=True, filter=True)
    grid_options = gb.build()
    
    # Display Trade Log using AgGrid
    AgGrid(
        trade_df.sort_values('Date').reset_index(drop=True),
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        height=400,
        theme='streamlit',  # Updated theme
    )

# ----------- Filter Trades by Stock -----------
elif selected_section == "Filter Trades by Stock":
    st.header("🔍 Filter Trades by Stock")
    
    # Dropdown for selecting a specific stock or all
    selected_stock = st.selectbox(
        'Select a stock to filter trades:',
        ['All'] + sorted(trade_df['Stock'].unique())
    )
    
    # Filter the trade log based on selection
    if selected_stock != 'All':
        filtered_trades = trade_df[trade_df['Stock'] == selected_stock]
    else:
        filtered_trades = trade_df
    
    # Display the filtered trades
    st.subheader(f"Trade Log: {'All Stocks' if selected_stock == 'All' else selected_stock}")
    
    # Configure AgGrid Options for filtered trades
    gb_filtered = GridOptionsBuilder.from_dataframe(filtered_trades)
    gb_filtered.configure_pagination(paginationAutoPageSize=True)
    gb_filtered.configure_side_bar()
    gb_filtered.configure_default_column(editable=False, sortable=True, filter=True)
    grid_options_filtered = gb_filtered.build()
    
    # Display Filtered Trade Log using AgGrid
    AgGrid(
        filtered_trades.sort_values('Date').reset_index(drop=True),
        gridOptions=grid_options_filtered,
        enable_enterprise_modules=True,
        height=400,
        theme='streamlit',  # Updated theme
    )

# ----------- Additional Enhancements: Date Range Filter -----------
# Adding a date range filter to dynamically update Portfolio vs SPY performance charts

# Add a horizontal divider
st.markdown("---")

st.header("🗓️ Select Date Range for Performance Analysis")

# Define the minimum and maximum dates from the portfolio data
min_date = portfolio_df['Date'].min().date()
max_date = portfolio_df['Date'].max().date()

# Date range selection using streamlit's date_input
start_date_filter, end_date_filter = st.date_input(
    "Select start and end dates:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Ensure that start_date_filter and end_date_filter are of datetime type
# Convert them to pd.Timestamp for consistent comparison
if isinstance(start_date_filter, date):
    start_date_filter = pd.to_datetime(start_date_filter)
if isinstance(end_date_filter, date):
    end_date_filter = pd.to_datetime(end_date_filter)

# Filter the portfolio and SPY data based on the selected date range
filtered_portfolio = portfolio_df[
    (portfolio_df['Date'] >= start_date_filter) &
    (portfolio_df['Date'] <= end_date_filter)
]

# Check if there is data in the selected range
if not filtered_portfolio.empty:
    # Updated Portfolio vs SPY Performance Chart with filtered data
    st.header("📈 Filtered Portfolio vs SPY Performance")
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=filtered_portfolio['Date'],
        y=filtered_portfolio['Portfolio Return'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='blue')
    ))
    fig3.add_trace(go.Scatter(
        x=filtered_portfolio['Date'],
        y=filtered_portfolio['SPY Return'],
        mode='lines',
        name='SPY Value',
        line=dict(color='orange')
    ))
    fig3.update_layout(
        title='Filtered Portfolio vs SPY Performance',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Updated Daily Portfolio Value Chart with filtered data
    st.header("📈 Filtered Daily Portfolio Value Over Time")
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=filtered_portfolio['Date'],
        y=filtered_portfolio['Portfolio Value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='green')
    ))
    fig4.update_layout(
        title='Filtered Daily Portfolio Value Over Time',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("No data available for the selected date range. Please adjust the dates.")

# ----------- Footer -----------
st.markdown("""
---
**Created by:** Your Name  
**Project:** Rotational Trading System  
**Date:** 2024-09-26
""")