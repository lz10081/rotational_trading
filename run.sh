#!/bin/bash

# Run the backtest script
echo "Running backtest.py..."
python backtest.py

# Check if the backtest was successful
if [ $? -eq 0 ]; then
    echo "Backtest completed successfully."
    echo "Starting Streamlit app..."
    # Run the Streamlit app
    streamlit run app.py
else
    echo "Backtest failed. Please check for errors."
fi