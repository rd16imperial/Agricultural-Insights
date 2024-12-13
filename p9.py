import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import plotly.graph_objects as go
from dash import Dash, dcc, html
import plotly.express as px
from dash.dependencies import Input, Output

# Load your data (replace with actual path or connection)
# Example: merged_data = pd.read_csv('your_file.csv')
merged_data = pd.read_csv('merged_data.csv')  # Ensure your file is loaded here

# Prepare features and target for machine learning
features = ["soilm_0_10cm", "soilm_10_40cm", "precip", "temperature", "humidity", "wind_speed", "evapotranspiration"]
target = "crop_yield"

# Add a computed crop_yield column (replace with your formula)
merged_data["crop_yield"] = (
    10 * merged_data["soilm_0_10cm"].astype(float) +
    5 * merged_data["precip"].astype(float) -
    2 * merged_data["temperature"].astype(float)
)

X = merged_data[features]
y = merged_data[target]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest
rf = RandomForestRegressor(random_state=42, n_estimators=100)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

# Feature importance
feature_importances = pd.DataFrame({
    "Feature": features,
    "Importance": rf.feature_importances_
}).sort_values(by="Importance", ascending=False)

# Dash App
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Agricultural Insights Dashboard", style={"textAlign": "center"}),

    # Seasonal Decomposition Plots
    html.Div([
        html.H2("Seasonal Decomposition"),
        dcc.Graph(id='seasonal-decomposition'),
        dcc.Dropdown(
            id='decomposition-dropdown',
            options=[{"label": col, "value": col} for col in ["soilm_0_10cm", "soilm_10_40cm", "soilm_40_100cm", "soilm_100_200cm"]],
            value="soilm_0_10cm",
            placeholder="Select Soil Factor"
        )
    ]),

    # Cross-Correlation Plots
    html.Div([
        html.H2("Cross-Correlation"),
        dcc.Graph(id='cross-correlation'),
        dcc.Dropdown(
            id='cross-corr-dropdown',
            options=[
                {"label": f"soilm_0_10cm vs {other}", "value": other}
                for other in ["soilm_10_40cm", "soilm_40_100cm", "soilm_100_200cm"]
            ],
            value="soilm_10_40cm",
            placeholder="Select Soil Pair"
        )
    ]),

    # Feature Importance Plot
    html.Div([
        html.H2("Feature Importance"),
        dcc.Graph(
            figure=px.bar(
                feature_importances,
                x="Feature",
                y="Importance",
                title="Feature Importance for Crop Yield Prediction",
                color="Importance"
            )
        )
    ]),

    # Bubble Chart
    html.Div([
        html.H2("Bubble Chart of Cross-Dataset Correlations"),
        dcc.Graph(
            figure=px.scatter(
                x=["pressure", "humidity", "precipitation", "temperature"],
                y=["soilt_100_200cm", "wind_10m_spd_avg", "soilt_40_100cm", "skin_temp_avg"],
                size=[0.86, 0.4, 0.5, 0.6],  # Replace with actual correlation data
                color=[0.86, 0.4, 0.5, 0.6],
                labels={"x": "Weather Factor", "y": "Soil Factor", "size": "Correlation"},
                title="Bubble Chart of Top Cross-Dataset Correlations"
            )
        )
    ])
])

# Callbacks for Interactivity
@app.callback(
    Output('seasonal-decomposition', 'figure'),
    [Input('decomposition-dropdown', 'value')]
)
def update_seasonal_decomposition(selected_factor):
    # Perform seasonal decomposition
    result = seasonal_decompose(merged_data[selected_factor], model="additive", period=2)
    observed = result.observed
    trend = result.trend
    seasonal = result.seasonal
    resid = result.resid

    # Create Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=observed, mode='lines', name='Observed'))
    fig.add_trace(go.Scatter(y=trend, mode='lines', name='Trend'))
    fig.add_trace(go.Scatter(y=seasonal, mode='lines', name='Seasonality'))
    fig.add_trace(go.Scatter(y=resid, mode='lines', name='Residuals'))
    fig.update_layout(title=f"Seasonal Decomposition of {selected_factor}", xaxis_title="Time", yaxis_title="Value")
    return fig


@app.callback(
    Output('cross-correlation', 'figure'),
    [Input('cross-corr-dropdown', 'value')]
)
def update_cross_correlation(selected_pair):
    # Compute cross-correlation
    lagged_corr = np.correlate(
        merged_data["soilm_0_10cm"] - merged_data["soilm_0_10cm"].mean(),
        merged_data[selected_pair] - merged_data[selected_pair].mean(),
        mode='full'
    )

    # Create Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=lagged_corr, mode='lines', name=f"Cross-Correlation: soilm_0_10cm vs {selected_pair}"))
    fig.update_layout(title=f"Cross-Correlation of soilm_0_10cm vs {selected_pair}", xaxis_title="Lag", yaxis_title="Correlation")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
