import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "MILV Ops Dashboard POC/MVP v1"

# Load your data
file_path = 'C:/Users/aliso/OneDrive/Desktop/Cleaned_Operational_Data.csv'  # Update this path with the correct file path
data = pd.read_csv(file_path)

# Remove columns with "Unnamed" in their name
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

# Prepare unique values for filtering
unique_employment_types = data['FY25 Employment'].unique()
unique_categories = data['Category'].unique()
unique_subcategories = data['Subcategory'].unique()
numerical_columns = data.select_dtypes(include='number').columns

# Main layout of the dashboard
app.layout = html.Div(
    style={'padding': '20px'},
    children=[
        html.H1("MILV Ops Dashboard POC/MVP v1", style={'textAlign': 'center'}),

        # Filters
        html.Div([
            html.Label("Filter by Employment Type:"),
            dcc.Dropdown(
                id='employment-filter',
                options=[{'label': emp, 'value': emp} for emp in unique_employment_types],
                multi=True
            ),

            html.Label("Filter by Doctor:"),
            dcc.Dropdown(
                id='doctor-filter',
                multi=True
            ),

            html.Label("Filter by Category:"),
            dcc.Dropdown(
                id='category-filter',
                options=[{'label': cat, 'value': cat} for cat in unique_categories],
                multi=True
            ),

            html.Label("Filter by Subcategory:"),
            dcc.Dropdown(
                id='subcategory-filter',
                multi=True
            ),

            html.Label("Select Values to Display:"),
            dcc.Dropdown(
                id='value-selector',
                options=[{'label': col, 'value': col} for col in numerical_columns],
                multi=True
            ),

            html.Label("Select Chart Type:"),
            dcc.Dropdown(
                id='chart-type-selector',
                options=[
                    {'label': 'Bar', 'value': 'Bar'},
                    {'label': 'Line', 'value': 'Line'},
                    {'label': 'Scatter', 'value': 'Scatter'}
                ],
                value='Bar'
            )
        ], style={'marginBottom': '20px'}),

        # Display the graph
        html.Div(id='graph-output')
    ]
)

# Callback to update doctor options based on selected employment type
@app.callback(
    Output('doctor-filter', 'options'),
    [Input('employment-filter', 'value')]
)
def update_doctor_options(selected_employment):
    if selected_employment:
        filtered_data = data[data['FY25 Employment'].isin(selected_employment)]
        doctors = filtered_data['Dr'].unique()
    else:
        doctors = data['Dr'].unique()
    return [{'label': doc, 'value': doc} for doc in doctors]

# Callback to update subcategory options based on selected category
@app.callback(
    Output('subcategory-filter', 'options'),
    [Input('category-filter', 'value')]
)
def update_subcategory_options(selected_categories):
    if selected_categories:
        filtered_data = data[data['Category'].isin(selected_categories)]
        subcategories = filtered_data['Subcategory'].unique()
    else:
        subcategories = data['Subcategory'].unique()
    return [{'label': subcat, 'value': subcat} for subcat in subcategories]

# Callback to update the graph with conditional aggregation
@app.callback(
    Output('graph-output', 'children'),
    [Input('employment-filter', 'value'),
     Input('doctor-filter', 'value'),
     Input('category-filter', 'value'),
     Input('subcategory-filter', 'value'),
     Input('value-selector', 'value'),
     Input('chart-type-selector', 'value')]
)
def update_graph(selected_employment, selected_doctors, selected_categories, selected_subcategories, selected_values, chart_type):
    # Copy the data for filtering
    filtered_data = data.copy()
    
    # Filter by employment type if selected
    if selected_employment:
        filtered_data = filtered_data[filtered_data['FY25 Employment'].isin(selected_employment)]
    
    # Filter by category if selected
    if selected_categories:
        filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]
    
    # Filter by subcategory if selected
    if selected_subcategories:
        filtered_data = filtered_data[filtered_data['Subcategory'].isin(selected_subcategories)]

    # Check if values are selected for the graph
    if not selected_values:
        return html.Div("Please select values to display on the graph.", style={'textAlign': 'center', 'color': 'red'})

    # Create the graph figure
    figure = go.Figure()

    # If doctors are selected, display data per doctor
    if selected_doctors:
        for doctor in selected_doctors:
            doctor_data = filtered_data[filtered_data['Dr'] == doctor]
            for value in selected_values:
                if value in doctor_data.columns:
                    figure.add_trace(go.Bar(x=doctor_data['Subcategory'], y=doctor_data[value], name=f"{doctor} - {value}"))
    else:
        # If no specific doctors are selected, aggregate by 'FY25 Employment'
        if selected_employment:
            aggregated_data = filtered_data.groupby('FY25 Employment', as_index=False).sum()
            for value in selected_values:
                if value in aggregated_data.columns:
                    figure.add_trace(go.Bar(x=aggregated_data['FY25 Employment'], y=aggregated_data[value], name=value))
        else:
            # Prompt to select an option if nothing is selected
            return html.Div("Please select either doctors or an employment type for comparison.", style={'textAlign': 'center', 'color': 'red'})

    # Update the figure layout
    figure.update_layout(
        title="Comparison of wRVU Values",
        xaxis_title="Subcategory" if selected_doctors else "Employment Type",
        yaxis_title="Values",
        legend_title="Metrics",
        showlegend=True
    )
    
    return dcc.Graph(figure=figure)

# Run the app on port 8080
if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
