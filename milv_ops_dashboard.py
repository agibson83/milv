import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the data
file_path = '/path/to/your/alison-ops-analysisv3.xlsx'  # Update with the correct path
data = pd.read_excel(file_path, sheet_name='alison-ops-analysis')

# Create a Dash app
app = dash.Dash(__name__)

# Extract unique values for multi-selection
providers = data['Dr'].unique()
categories = data['Category'].unique()

# Define the layout of the app
app.layout = html.Div([
    html.H1("MILV Ops Dashboard POC/MVP v1", style={'text-align': 'center', 'font-family': 'Arial, sans-serif'}),
    
    html.Div([
        html.Label("Select Providers:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='provider-dropdown',
            options=[{'label': provider, 'value': provider} for provider in providers],
            value=providers[:3],  # Default to the first three providers
            multi=True
        ),
    ], style={'padding': '10px'}),
    
    html.Div([
        html.Label("Select Categories:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': category, 'value': category} for category in categories],
            value=categories[:2],  # Default to the first two categories
            multi=True
        ),
    ], style={'padding': '10px'}),
    
    dcc.Graph(id='wrvu-trend-graph'),
    dcc.Graph(id='payments-trend-graph'),
    dcc.Graph(id='cf-trend-graph')
], style={'max-width': '1200px', 'margin': 'auto'})

# Define callback functions
@app.callback(
    [Output('wrvu-trend-graph', 'figure'),
     Output('payments-trend-graph', 'figure'),
     Output('cf-trend-graph', 'figure')],
    [Input('provider-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_graphs(selected_providers, selected_categories):
    # Filter data based on multi-selections
    filtered_data = data[data['Dr'].isin(selected_providers) & data['Category'].isin(selected_categories)]
    
    # Create WRVU trend graph
    wrvu_fig = px.line(
        filtered_data,
        x=['Total WRVU FY22', 'Total WRVU FY23', 'Total WRVU FY24'],
        y=filtered_data[['Total WRVU FY22', 'Total WRVU FY23', 'Total WRVU FY24']].values.flatten(),
        labels={'x': 'Fiscal Year', 'y': 'Total WRVU'},
        title='Total WRVU Trend',
        markers=True
    )
    wrvu_fig.update_layout(title_font_size=18, font_family="Arial, sans-serif")
    
    # Create Payments trend graph
    payments_fig = px.line(
        filtered_data,
        x=['Total Payments FY22', 'Total Payments FY23', 'Total Payments FY24'],
        y=filtered_data[['Total Payments FY22', 'Total Payments FY23', 'Total Payments FY24']].values.flatten(),
        labels={'x': 'Fiscal Year', 'y': 'Total Payments ($)'},
        title='Total Payments Trend',
        markers=True
    )
    payments_fig.update_layout(title_font_size=18, font_family="Arial, sans-serif")
    
    # Create CF (Conversion Factor) trend graph
    cf_fig = px.line(
        filtered_data,
        x=['CF FY22', 'CF FY23', 'CF FY24'],
        y=filtered_data[['CF FY22', 'CF FY23', 'CF FY24']].values.flatten(),
        labels={'x': 'Fiscal Year', 'y': 'Conversion Factor (CF)'},
        title='Conversion Factor Trend',
        markers=True
    )
    cf_fig.update_layout(title_font_size=18, font_family="Arial, sans-serif")
    
    return wrvu_fig, payments_fig, cf_fig

# Run the app on port 8080
if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
