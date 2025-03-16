'''
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


pip install dash pandas plotly
'''

import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output

# Load dataset
df = pd.read_csv('spotify_data.csv', encoding='utf-8')


# Extracting numerical columns, for correlaion and other relationships between features
numerical_columns = df.select_dtypes(include=['number']).columns.tolist()

# Unique artists to comparre two artists, their count of streams, likes, and views
artists = df["Artist"].unique()


# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    
    html.H2("Spotify Data Analysis Dashboard App", style={'textAlign': 'center', 'color': '#2c3e50'}),

    html.Hr(),
    
# 2 Artists Comparision-html
    html.Div([
        html.H3("Compare Two Artists", style = {'textAlign': 'center'}),

        html.Label("Select First Artist:", style = {'fontSize':'16px', 'fontWeight':'bold'}),
        
        dcc.Dropdown(
            id = "artist1", 
            options = [{"label": a, "value": a} for a in artists], 
            value = artists[0], 
            style = {'width': '65%', 'marginBottom': '10px'}),

        html.Label("Select Second Artist:", style = {'fontSize': '16px', 'fontWeight': 'bold'}),
        
        dcc.Dropdown(
            id = "artist2", 
            options = [{"label": a, "value": a} for a in artists], 
            value = artists[1] if len(artists) >  1 else artists[0], 
            style={'width': '65%', 'marginBottom': '20px'}),

        dcc.Graph(id = "comparison-graph")
    ], style = {'width': '80%', 'margin': 'auto'}),

    html.Hr(),


# Top 5 Songs of An Artist, Bar Chart - html
    html.Div([

        html.H3("Top 5 Songs of An Artist", style={'textAlign': 'center', 'color': '#2c3e50'}), 

        html.Label("Select an Artist:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='artist-dropdown',
            options=[{'label': artist, 'value': artist} for artist in df["Artist"].unique()],
            value=df["Artist"].unique()[0],
            style={'width': '50%', 'marginBottom': '10px'}
        ),
        dcc.Graph(id='top-songs-bar')
    ], style={'width': '80%', 'margin': 'auto'}),

    html.Hr(),

# For Distribution Graph - html
    html.Div([

        html.H3("Distribution Graph", style={'textAlign': 'center', 'color': '#2c3e50'}),            

        html.Label("Select a Feature for Distribution:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='distribution-dropdown',
            options=[{'label': col, 'value': col} for col in numerical_columns],
            value=numerical_columns[0],
            style={'width': '50%', 'marginBottom': '10px'}
        ),
        dcc.Graph(id='distribution-graph')
    ], style={'width': '80%', 'margin': 'auto'}),

    html.Hr(),

# Heatmap correlation - html
    html.Div([
        html.H3("Correlation Heatmap", style={'textAlign': 'center', 'color': '#2c3e50'}),
        dcc.Graph(id='heatmap-graph')
    ], style={'width': '80%', 'margin': 'auto'}),

    html.Hr(),

# Feature Relationship (Two Feature Correlation)
    html.Div([
        html.H3("Feature Correlation", style={'textAlign': 'center', 'color': '#2c3e50'}),

        html.Div([
            html.Label("Select First Feature:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='feature-x-dropdown',
                options=[{'label': col, 'value': col} for col in numerical_columns],
                value=numerical_columns[0],
                style={'width': '45%', 'display': 'inline-block', 'marginRight': '5%'}
            ),

            html.Label("Select Second Feature:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='feature-y-dropdown',
                options=[{'label': col, 'value': col} for col in numerical_columns],
                value=numerical_columns[1],
                style={'width': '45%', 'display': 'inline-block'}
            ),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '20px'}),

        dcc.Graph(id='correlation-graph')

    ], style={'width': '80%', 'margin': 'auto'}),

    html.Hr(),

    html.H3("A plotly dashboard app.", style={'textAlign': 'center', 'color': '#2c3e50'})

])

# Callback for to update Artist comparision
@app.callback(
        Output("comparison-graph", "figure"), # If the graph is fixed (does not depend on user input), we can set figure inside dcc.Graph itself.  No callback is needed for static graphs.
        [Input("artist1", "value"), Input("artist2", "value")]
)

def update_comparision_graph(artist1, artist2):
    filtered_df = df[df["Artist"].isin({artist1, artist2})]

    # Aggregate metrics
    comparison_df = filtered_df.groupby("Artist").agg({
        "Stream": "sum",
        "Likes": "sum",
        "Views": "sum",
    }).reset_index()

    comparison_df_melted = comparison_df.melt(id_vars = "Artist", var_name = "Metric", value_name = "value")
    # The .melt() function converts multiple columns into two new columns:
    # Metric: Holds the original column names (e.g., "Streams", "Likes").
    # value: Holds the corresponding values from the original columns.

    # Colors
    color_map = {"Stream": "#3F8FC4", "Likes": "#E74C3C", "Views": "#08306B"} 

    fig = px.bar(
        comparison_df_melted, x="Artist", y="value", color="Metric",
        barmode="group", color_discrete_map=color_map,
        title=f"Comparison: {artist1} vs {artist2}", template="plotly_white"
    )

    return fig

# Callback to update bar chart
@app.callback(
    Output('top-songs-bar', 'figure'),
    [Input('artist-dropdown', 'value')]
)
def update_bar_chart(selected_artist):
    filtered_df = df[df["Artist"] == selected_artist].nlargest(5, "Stream")
    fig = px.bar(filtered_df, x="Track", y="Stream", title=f"Top 5 Songs of {selected_artist}",
                 color="Stream", color_continuous_scale="Blues")
    return fig


# Callback to update distribution graph
@app.callback(
    Output('distribution-graph', 'figure'),
    [Input('distribution-dropdown', 'value')]
)
def update_distribution_graph(selected_column):
    fig = px.histogram(df, x=selected_column, title=f"Distribution of {selected_column}",
                       color_discrete_sequence=['#3498db'])
    return fig


# Callback to update heatmap
@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('artist-dropdown', 'value')]  
)
def update_heatmap(_):
    correlation_matrix = df[numerical_columns].corr() # only numerical features are used for heatmap
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale="Blues",
        zmin=-1, zmax=1
    ))
    
    fig.update_layout(title="Feature Correlation Heatmap", template="plotly_white")
    return fig


# Callback to update feature correlation graph
@app.callback(
    Output('correlation-graph', 'figure'),
    [Input('feature-x-dropdown', 'value'),
     Input('feature-y-dropdown', 'value')]
)
def update_correlation_graph(feature_x, feature_y):
    fig = px.scatter(df, x=feature_x, y=feature_y, title=f"Correlation: {feature_x} vs {feature_y}",
                     color_discrete_sequence=['#e74c3c'])
    
    fig.update_layout(template="plotly_white")
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


