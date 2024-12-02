import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
data_path = r'C:\Users\aliso\OneDrive\Desktop\MILV\Python\Above_Average_Turnaround.csv'
data = pd.read_csv(data_path)

# Ensure proper datetime parsing
data['Finalize Time'] = pd.to_datetime(data['Finalize Time'])
data['End Date'] = pd.to_datetime(data['End Date'])
data['Date'] = data['End Date'].dt.date

# Initialize the app
app = dash.Dash(__name__)
app.title = "Enhanced Turnaround Time Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Enhanced Turnaround Time Dashboard", style={'text-align': 'center'}),

    # Filters Section
    html.Div([
        # Date Range Filter
        html.Div([
            html.Label("Select Date Range:"),
            dcc.DatePickerRange(
                id='date-picker',
                start_date=data['Date'].min(),
                end_date=data['Date'].max(),
                display_format='YYYY-MM-DD'
            ),
        ], style={'margin-bottom': '20px', 'width': '48%', 'display': 'inline-block'}),

        # Modality Filter
        html.Div([
            html.Label("Filter by Modality:"),
            dcc.Dropdown(
                id='modality-dropdown',
                options=[{'label': mod, 'value': mod} for mod in data['Modality'].dropna().unique()],
                value=None,
                multi=True,
                placeholder="Select modality..."
            ),
        ], style={'margin-bottom': '20px', 'width': '48%', 'display': 'inline-block'}),

        # Hospital Location Filter
        html.Div([
            html.Label("Filter by Hospital Location:"),
            dcc.Dropdown(
                id='hospital-dropdown',
                options=[{'label': loc, 'value': loc} for loc in data['Hospital Location'].dropna().unique()],
                value=None,
                multi=True,
                placeholder="Select hospital location..."
            ),
        ], style={'margin-bottom': '20px', 'width': '48%', 'display': 'inline-block'}),
    ]),

    # Dropdown to Select Grouping Field
    html.Div([
        html.Label("Group by:"),
        dcc.Dropdown(
            id='grouping-dropdown',
            options=[
                {'label': 'Department', 'value': 'Department'},
                {'label': 'Modality', 'value': 'Modality'},
                {'label': 'Radiologist Group', 'value': 'Radiologist Group'}
            ],
            value='Department',
            multi=False,
            style={'width': '50%'}
        )
    ], style={'margin-bottom': '20px'}),

    # Heatmap
    html.Div([
        dcc.Graph(id='heatmap'),
    ]),

    # Line Chart for Trends
    html.Div([
        dcc.Graph(id='line-chart'),
    ]),

    # Data Table
    html.Div([
        html.H3("Detailed Records", style={'text-align': 'center'}),
        dash_table.DataTable(
            id='data-table',
            columns=[{'name': col, 'id': col} for col in data.columns],
            style_table={'overflowX': 'auto'},
            page_size=10,
        )
    ], style={'margin-top': '20px'}),

    # Export Button
    html.Div([
        html.Button("Download Filtered Data", id="download-button"),
        dcc.Download(id="download-dataframe-csv"),
    ], style={'text-align': 'center', 'margin-top': '20px'}),
])

# Callbacks
@app.callback(
    [Output('heatmap', 'figure'),
     Output('line-chart', 'figure'),
     Output('data-table', 'data')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('modality-dropdown', 'value'),
     Input('hospital-dropdown', 'value'),
     Input('grouping-dropdown', 'value')]
)
def update_visualizations(start_date, end_date, modalities, hospitals, group_by):
    # Filter data
    filtered_data = data[
        (data['Date'] >= pd.to_datetime(start_date).date()) &
        (data['Date'] <= pd.to_datetime(end_date).date())
    ]
    if modalities:
        filtered_data = filtered_data[filtered_data['Modality'].isin(modalities)]
    if hospitals:
        filtered_data = filtered_data[filtered_data['Hospital Location'].isin(hospitals)]

    # Heatmap
    heatmap_fig = px.density_heatmap(
        filtered_data,
        x='Date',
        y=group_by,
        z='Turnaround_Time_Hours',
        color_continuous_scale='Viridis',
        title=f"Heatmap of Turnaround Times by {group_by}",
        labels={'Turnaround_Time_Hours': 'Avg Turnaround Time (Hours)'}
    )

    # Line Chart
    daily_avg = filtered_data.groupby('Date')['Turnaround_Time_Hours'].mean().reset_index()
    line_chart_fig = px.line(
        daily_avg,
        x='Date',
        y='Turnaround_Time_Hours',
        title="Daily Average Turnaround Time",
        labels={'Turnaround_Time_Hours': 'Avg Turnaround Time (Hours)'}
    )

    # Update table data
    table_data = filtered_data.to_dict('records')

    return heatmap_fig, line_chart_fig, table_data

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
if __name__ == '__main__':
    app.run_server(debug=True)
