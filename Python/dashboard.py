import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
data_path = r'C:\Users\aliso\OneDrive\Desktop\MILV\Python\Above_Average_Turnaround.csv'
data = pd.read_csv(data_path)

# Ensure proper datetime parsing
data['Finalize Time'] = pd.to_datetime(data['Finalize Time'])
data['End Date'] = pd.to_datetime(data['End Date'])

# Calculate additional fields
data['Date'] = data['End Date'].dt.date

# Initialize the app
app = dash.Dash(__name__)
app.title = "Turnaround Time Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Turnaround Time Dashboard", style={'text-align': 'center'}),

    # Date Range Filter
    html.Div([
        html.Label("Select Date Range:"),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=data['Date'].min(),
            end_date=data['Date'].max(),
            display_format='YYYY-MM-DD'
        ),
    ], style={'margin-bottom': '20px'}),

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
])

# Callbacks
@app.callback(
    [Output('heatmap', 'figure'),
     Output('line-chart', 'figure')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('grouping-dropdown', 'value')]
)
def update_visualizations(start_date, end_date, group_by):
    # Filter data by date range
    filtered_data = data[(data['Date'] >= pd.to_datetime(start_date).date()) &
                         (data['Date'] <= pd.to_datetime(end_date).date())]

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

    return heatmap_fig, line_chart_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
