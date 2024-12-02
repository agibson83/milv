import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import os

# Load data
data_path = os.getenv('DATA_PATH', 'Above_Average_Turnaround.csv')  # Use an environment variable for the data path
data = pd.read_csv(data_path, low_memory=False)
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]  # Drop unnecessary columns
data['Finalize Time'] = pd.to_datetime(data['Finalize Time'])
data['End Date'] = pd.to_datetime(data['End Date'])
data['Date'] = data['End Date'].dt.date

# Initialize the app
app = dash.Dash(__name__)
app.title = "Executive Turnaround Time Dashboard"

# Layout
app.layout = html.Div([
    html.Div([
        html.H1("Turnaround Time Dashboard", style={'text-align': 'center', 'color': '#003366'}),
        html.P("Analyze and monitor turnaround times to identify bottlenecks and improve efficiency.",
               style={'text-align': 'center', 'color': '#666666'}),
    ], style={'padding': '20px', 'background-color': '#f2f2f2'}),

    # Summary Metrics
    html.Div([
        html.Div([
            html.H3("Average TAT (Hours)", style={'text-align': 'center'}),
            html.H1(id='avg-tat', style={'text-align': 'center', 'color': '#003366'}),
        ], className="summary-metric", style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.H3("Max TAT (Hours)", style={'text-align': 'center'}),
            html.H1(id='max-tat', style={'text-align': 'center', 'color': '#003366'}),
        ], className="summary-metric", style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.H3("Records Filtered", style={'text-align': 'center'}),
            html.H1(id='record-count', style={'text-align': 'center', 'color': '#003366'}),
        ], className="summary-metric", style={'width': '30%', 'display': 'inline-block'}),
    ], style={'padding': '20px', 'background-color': '#ffffff', 'border-bottom': '1px solid #cccccc'}),

    # Filters Section
    html.Div([
        html.Div([
            html.Label("Select Date Range:", style={'font-weight': 'bold'}),
            dcc.DatePickerRange(
                id='date-picker',
                start_date=data['Date'].min(),
                end_date=data['Date'].max(),
                display_format='YYYY-MM-DD',
            ),
        ], style={'margin-bottom': '20px', 'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Filter by Modality:", style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='modality-dropdown',
                options=[{'label': mod, 'value': mod} for mod in data['Modality'].dropna().unique()],
                value=None,
                multi=True,
                placeholder="Select modality...",
            ),
        ], style={'margin-bottom': '20px', 'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Filter by Hospital Location:", style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='hospital-dropdown',
                options=[{'label': loc, 'value': loc} for loc in data['Hospital Location'].dropna().unique()],
                value=None,
                multi=True,
                placeholder="Select hospital location...",
            ),
        ], style={'margin-bottom': '20px', 'width': '48%', 'display': 'inline-block'}),
    ], style={'padding': '20px', 'background-color': '#f2f2f2'}),

    # Visualizations Section
    html.Div([
        html.Div([
            dcc.Graph(id='heatmap'),
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='line-chart'),
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'padding': '20px'}),

    # Data Table Section
    html.Div([
        html.H3("Detailed Records", style={'text-align': 'center', 'color': '#003366'}),
        dash_table.DataTable(
            id='data-table',
            columns=[{'name': col, 'id': col} for col in data.columns],
            style_table={'overflowX': 'auto', 'margin': '20px'},
            page_size=10,
        ),
    ], style={'padding': '20px', 'background-color': '#ffffff', 'border-top': '1px solid #cccccc'}),

    # Export Button
    html.Div([
        html.Button("Download Filtered Data", id="download-button", style={'background-color': '#003366', 'color': 'white'}),
        dcc.Download(id="download-dataframe-csv"),
    ], style={'text-align': 'center', 'margin-top': '20px'}),
])

# Callbacks
@app.callback(
    [Output('avg-tat', 'children'),
     Output('max-tat', 'children'),
     Output('record-count', 'children'),
     Output('heatmap', 'figure'),
     Output('line-chart', 'figure'),
     Output('data-table', 'data')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('modality-dropdown', 'value'),
     Input('hospital-dropdown', 'value')]
)
def update_dashboard(start_date, end_date, modalities, hospitals):
    # Filter data
    filtered_data = data[
        (data['Date'] >= pd.to_datetime(start_date).date()) &
        (data['Date'] <= pd.to_datetime(end_date).date())
    ]
    if modalities:
        filtered_data = filtered_data[filtered_data['Modality'].isin(modalities)]
    if hospitals:
        filtered_data = filtered_data[filtered_data['Hospital Location'].isin(hospitals)]

    # Summary metrics
    avg_tat = f"{filtered_data['Turnaround_Time_Hours'].mean():.2f}" if not filtered_data.empty else "N/A"
    max_tat = f"{filtered_data['Turnaround_Time_Hours'].max():.2f}" if not filtered_data.empty else "N/A"
    record_count = len(filtered_data)

    # Heatmap
    heatmap_fig = px.density_heatmap(
        filtered_data,
        x='Date',
        y='Modality',
        z='Turnaround_Time_Hours',
        color_continuous_scale='Viridis',
        title="Heatmap of Turnaround Times by Modality",
        labels={'Turnaround_Time_Hours': 'Avg Turnaround Time (Hours)'},
    )

    # Line Chart
    daily_avg = filtered_data.groupby('Date')['Turnaround_Time_Hours'].mean().reset_index()
    line_chart_fig = px.line(
        daily_avg,
        x='Date',
        y='Turnaround_Time_Hours',
        title="Daily Average Turnaround Time",
        labels={'Turnaround_Time_Hours': 'Avg Turnaround Time (Hours)'},
    )

    # Update table data
    table_data = filtered_data.to_dict('records')

    return avg_tat, max_tat, record_count, heatmap_fig, line_chart_fig, table_data

@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("download-button", "n_clicks"),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('modality-dropdown', 'value'),
     Input('hospital-dropdown', 'value')]
)
def download_filtered_data(n_clicks, start_date, end_date, modalities, hospitals):
    if n_clicks is None:
        return dash.no_update

    # Filter data for export
    filtered_data = data[
        (data['Date'] >= pd.to_datetime(start_date).date()) &
        (data['Date'] <= pd.to_datetime(end_date).date())
    ]
    if modalities:
        filtered_data = filtered_data[filtered_data['Modality'].isin(modalities)]
    if hospitals:
        filtered_data = filtered_data[filtered_data['Hospital Location'].isin(hospitals)]

    return dcc.send_data_frame(filtered_data.to_csv, "Filtered_Data.csv")

# Run the app
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
