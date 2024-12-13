import dash
from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# Firebase Initialization
cred = credentials.Certificate("crop-yeild-project-firebase-adminsdk-rqplp-e61c3c5737.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Fetch Weather Data from Firestore
def fetch_weather_data():
    collection_ref = db.collection("weather_data")
    docs = collection_ref.stream()
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    return data

# Fetch Soil and Weather Data from Firestore
def fetch_soil_weather_data():
    collection_ref = db.collection("daily_soil_weather_data")
    docs = collection_ref.stream()
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    return data

# Convert Firestore Data to DataFrame
weather_data = fetch_weather_data()
soil_weather_data = fetch_soil_weather_data()

if weather_data:
    weather_df = pd.DataFrame(weather_data)
    if 'timestamp' in weather_df.columns:
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
else:
    weather_df = pd.DataFrame()

if soil_weather_data:
    soil_weather_df = pd.DataFrame(soil_weather_data)
    # Convert numeric columns from strings to proper types
    for col in soil_weather_df.columns:
        if col not in ['timestamp_local', 'timestamp_utc']:
            soil_weather_df[col] = pd.to_numeric(soil_weather_df[col], errors='coerce')
    soil_weather_df['timestamp_local'] = pd.to_datetime(soil_weather_df['timestamp_local'])
else:
    soil_weather_df = pd.DataFrame()

# Dash App Setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([
    html.H1("Weather and Soil Data Dashboard", className="text-center text-primary mb-4"),

    # Weather Data Section
    dbc.Card([
        dbc.CardBody([
            html.H4("Weather Data", className="card-title"),
            html.Label("Select Weather Parameter to Visualize:"),
            dcc.Dropdown(
                id='weather-y-axis-dropdown',
                options=[
                    {'label': col, 'value': col}
                    for col in weather_df.select_dtypes(include=['float64', 'int64']).columns
                ],
                value='temperature',  # Default value
                className="mb-3"
            ),
            dcc.Graph(id='weather-line-graph')
        ])
    ], className="mb-4"),

    # Soil and Weather Data Section
    dbc.Card([
        dbc.CardBody([
            html.H4("Soil and Weather Data", className="card-title"),
            html.Label("Select Soil and Weather Parameter to Visualize:"),
            dcc.Dropdown(
                id='soil-weather-y-axis-dropdown',
                options=[
                    {'label': col, 'value': col}
                    for col in soil_weather_df.select_dtypes(include=['float64', 'int64']).columns
                ],
                value='evapotranspiration',  # Default value
                className="mb-3"
            ),
            dcc.Graph(id='soil-weather-line-graph')
        ])
    ], className="mb-4"),

    # Cross-Parameter Dual Line Graph Section
    dbc.Card([
        dbc.CardBody([
            html.H4("Dual Line Graph Comparison", className="card-title"),
            html.Label("Select First Parameter:"),
            dcc.Dropdown(
                id='dual-line-param1-dropdown',
                options=[
                    {'label': col, 'value': col}
                    for col in list(weather_df.select_dtypes(include=['float64', 'int64']).columns) +
                                list(soil_weather_df.select_dtypes(include=['float64', 'int64']).columns)
                ],
                className="mb-3"
            ),
            html.Label("Select Second Parameter:"),
            dcc.Dropdown(
                id='dual-line-param2-dropdown',
                options=[
                    {'label': col, 'value': col}
                    for col in list(weather_df.select_dtypes(include=['float64', 'int64']).columns) +
                                list(soil_weather_df.select_dtypes(include=['float64', 'int64']).columns)
                ],
                className="mb-3"
            ),
            dcc.Graph(id='dual-line-graph')
        ])
    ], className="mb-4")
], fluid=True)

# Callback to Update Weather Graph
@app.callback(
    dash.dependencies.Output('weather-line-graph', 'figure'),
    [dash.dependencies.Input('weather-y-axis-dropdown', 'value')]
)
def update_weather_graph(selected_param):
    if selected_param and not weather_df.empty:
        fig = px.line(
            weather_df, 
            x='timestamp', 
            y=selected_param, 
            title=f"Weather Data: {selected_param} Over Time",
            template='plotly_dark',
            color_discrete_sequence=['#636EFA']
        )
        fig.update_layout(
            paper_bgcolor='#1e2130',
            plot_bgcolor='#1e2130',
            font=dict(color='white')
        )
        return fig
    return {}

# Callback to Update Soil and Weather Graph
@app.callback(
    dash.dependencies.Output('soil-weather-line-graph', 'figure'),
    [dash.dependencies.Input('soil-weather-y-axis-dropdown', 'value')]
)
def update_soil_weather_graph(selected_param):
    if selected_param and not soil_weather_df.empty:
        fig = px.line(
            soil_weather_df, 
            x='timestamp_local', 
            y=selected_param, 
            title=f"Soil and Weather Data: {selected_param} Over Time",
            template='plotly_dark',
            color_discrete_sequence=['#EF553B']
        )
        fig.update_layout(
            paper_bgcolor='#1e2130',
            plot_bgcolor='#1e2130',
            font=dict(color='white')
        )
        return fig
    return {}

# Callback to Update Dual Line Graph
@app.callback(
    dash.dependencies.Output('dual-line-graph', 'figure'),
    [dash.dependencies.Input('dual-line-param1-dropdown', 'value'),
     dash.dependencies.Input('dual-line-param2-dropdown', 'value')]
)
def update_dual_line_graph(param1, param2):
    if param1 and param2 and not weather_df.empty and not soil_weather_df.empty:
        combined_df = pd.concat([weather_df, soil_weather_df], axis=1)
        fig = px.line(
            combined_df, 
            x='timestamp',
            y=[param1, param2], 
            title=f"Comparison: {param1} and {param2} Over Time",
            template='plotly_dark'
        )
        fig.update_traces(line_shape='linear')
        fig.update_layout(
            paper_bgcolor='#1e2130',
            plot_bgcolor='#1e2130',
            font=dict(color='white'),
            legend_title_text='Parameters'
        )
        return fig
    return {}

if __name__ == '__main__':
    app.run_server(debug=True)
