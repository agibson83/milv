import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os

# Load data
data_path = os.getenv('DATA_PATH', 'Above_Average_Turnaround.csv')  # Default to local file if env var not set
data = pd.read_csv(data_path, low_memory=False)
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]  # Drop unnecessary columns
data['Finalize Time'] = pd.to_datetime(data['Finalize Time'])
data['End Date'] = pd.to_datetime(data['End Date'])
data['Date'] = data['End Date'].dt.date

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Executive Turnaround Time Dashboard"

# Layout
app.layout = html.Div([
    html.Div([
        html.H1("Turnaround Time Dashboard", style={'text-align': 'center', 'color': '#003366'}),
        html.P("Analyze and monitor turnaround times to identify bottlenecks and improve efficiency.",
               style={'text-align': 'center', 'color': '#666666'}),
    ], style={'padding': '20px', 'background-color': '#f2f2f2'}),

    html.Div([
        html.Label("Select Date Range:", style={'font-weight': 'bold'}),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=data['Date'].min(),
            end_date=data['Date'].max(),
            display_format='YYYY-MM-DD',
        ),
    ], style={'margin-bottom': '20px'}),
])

# Allow deployment via Waitress
if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 8080))  # Get port from environment for Render
    serve(app, host="0.0.0.0", port=port)
