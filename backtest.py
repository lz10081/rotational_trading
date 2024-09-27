import pandas as pd
import numpy as np
import yfinance as yf
import datetime

def run_backtest():
    # Define parameters
    stocks = [
        'TSLA', 'NFLX', 'AAPL', 'NVDA', 'AMZN', 
        'MSFT', 'GOOG', 'AMD', 'INTC', 'META', 
        'SPY', 'QQQ', 'IWM','PLTR','COIN'
    ]
    start_date = '2024-09-05'
    #start_date = '2020-01-01'
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)

    end_date = today
    initial_capital = 100000

    # Download historical data
    data = yf.download(stocks, start=start_date, end=tomorrow)['Adj Close'].fillna(method='ffill')

    # Calculate 20-day ROC
    roc = data.pct_change(periods=15) * 100

    # Initialize portfolio
    capital = initial_capital
    positions = {}
    trade_log = []
    portfolio_history = []

    # Iterate over each trading day
    for current_date in roc.index[15:]:
        today_roc = roc.loc[current_date].dropna()
        top_stocks = today_roc.sort_values(ascending=False).head(5).index.tolist()

        # Select top 2 stocks for investment
        selected = today_roc.loc[top_stocks].sort_values(ascending=False).head(2).index.tolist()

        # Identify stocks to liquidate (not in top 5 ROC)
        to_liquidate = [stock for stock in positions if stock not in top_stocks]
        for stock in to_liquidate:
            exit_price = data.loc[current_date, stock]
            position = positions.pop(stock)  # Retrieve position details
            entry_price = position['entry_price']
            shares = position['shares']
            profit = shares * (exit_price - entry_price)
            capital += shares * exit_price
            trade_log.append({
                'Date': current_date,
                'Stock': stock,
                'Action': 'Sell',
                'Exit Price': round(exit_price, 2),
                'Shares': shares,
                'Profit': round(profit, 2)
            })

        # Determine current open positions to maintain exactly two
        current_positions = set(positions.keys())
        selected_to_buy = [stock for stock in selected if stock not in current_positions]

        # Calculate available slots for new positions
        available_slots = 2 - len(current_positions)

        # Only buy as many as available slots (should be up to 2)
        stocks_to_buy = selected_to_buy[:available_slots]

        for stock in stocks_to_buy:
            allocation = capital * 0.5  # Allocate 50% of current capital to each stock
            entry_price = data.loc[current_date, stock]
            shares = allocation // entry_price  # Integer number of shares
            cost = shares * entry_price
            if shares > 0:
                capital -= cost
                positions[stock] = {'entry_price': entry_price, 'shares': shares}
                trade_log.append({
                    'Date': current_date,
                    'Stock': stock,
                    'Action': 'Buy',
                    'Entry Price': round(entry_price, 2),
                    'Shares': shares
                })

        # Calculate current portfolio value
        portfolio_value = capital
        for stock, info in positions.items():
            current_price = data.loc[current_date, stock]
            portfolio_value += info['shares'] * current_price
        portfolio_history.append({'Date': current_date, 'Portfolio Value': portfolio_value})

    # Convert trade log and portfolio history to DataFrames
    trade_df = pd.DataFrame(trade_log)
    portfolio_df = pd.DataFrame(portfolio_history).set_index('Date')

    # Calculate final portfolio value by liquidating remaining positions
    for stock, info in positions.items():
        final_price = data.iloc[-1][stock]
        profit = (final_price - info['entry_price']) * info['shares']
        capital += info['shares'] * final_price
        trade_df = trade_df.append({
            'Date': data.index[-1],
            'Stock': stock,
            'Action': 'Sell',
            'Exit Price': round(final_price, 2),
            'Shares': info['shares'],
            'Profit': round(profit, 2)
        }, ignore_index=True)
        portfolio_value = capital
        portfolio_history.append({'Date': data.index[-1], 'Portfolio Value': portfolio_value})

    # Final metrics
    final_capital = capital
    total_profit = final_capital - initial_capital

    # Calculate SPY performance
    spy_data = yf.download('SPY', start=start_date, end=end_date)['Adj Close'].fillna(method='ffill')
    spy_df = spy_data.to_frame()
    spy_df = spy_df.rename(columns={'Adj Close': 'SPY'})
    spy_df = spy_df.merge(portfolio_df, left_index=True, right_index=True, how='left').fillna(method='ffill')
    spy_df['SPY Return'] = (spy_df['SPY'] / spy_df['SPY'].iloc[0]) * initial_capital

    # Calculate portfolio performance
    portfolio_df = portfolio_df.merge(spy_df['SPY Return'], left_index=True, right_index=True)
    portfolio_df['Portfolio Return'] = portfolio_df['Portfolio Value']

    # Final Summary
    summary = {
        'Final Portfolio Value': round(final_capital, 2),
        'Total Profit': round(total_profit, 2),
        'SPY Return (%)': round(((spy_data[-1] / spy_data[0]) - 1) * 100, 2)
    }

    # Prepare DataFrames for Streamlit
    portfolio_df.reset_index(inplace=True)
    spy_df.reset_index(inplace=True)

    # Save results to CSV for Streamlit to read
    portfolio_df.to_csv('portfolio_history.csv', index=False)
    trade_df.to_csv('trade_log.csv', index=False)
    summary_df = pd.DataFrame({
        'Metric': ['Final Portfolio Value', 'Total Profit', 'SPY Return (%)'],
        'Value': [summary['Final Portfolio Value'],
                  summary['Total Profit'],
                  summary['SPY Return (%)']]
    })
    summary_df.to_csv('summary.csv', index=False)

if __name__ == "__main__":
    run_backtest()