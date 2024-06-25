import pandas as pd
import dash
from dash import Dash, Input, Output, dcc, html
import os
from sqlalchemy import create_engine
import plotly.graph_objs as go
import plotly.io as pio
import io
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv  # Add this line


# Load environment variables from .env file
load_dotenv()

# Construct database URL from environment variables
#db_url = f"{os.getenv("ENGINE")}://{os.getenv('DTABASE_USER')}:{os.getenv('PASSWORD')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('ASI_DATABASE')}"
db_url =  create_engine(f'{os.getenv("ENGINE")}://{os.getenv("DTABASE_USER")}:{os.getenv("PASSWORD")}@{os.getenv("HOST")}/{os.getenv("ASI_DATABASE")}')

query = '''
    SELECT 
        af.indicator_code,
        af.state_code,
        af.nic_code,
        af.nic_code_type,
        af.indicator_value,
        af.financial_year,
        i.description AS indicator_description,
        i.unit AS unit_description,  -- Include the unit column
        n.description AS nic_description,
        s.description AS state_description
    FROM 
        asi_fact AS af
    JOIN 
        indicator AS i ON af.indicator_code = i.indicator_code
    JOIN 
        nic AS n ON af.nic_code = n.nic_code
    JOIN
        state AS s ON af.state_code = s.state_code
    WHERE af.nic_code = '99999'
    ORDER BY 
        af.financial_year
'''

df = pd.read_sql_query(query, db_url)
df1 = pd.read_csv(r'C:\Users\T18\cpigraph\cpigraph\asi\code\asi_indicator.csv', sep=',')

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
    {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets, routes_pathname_prefix = '/viz/asi/', requests_pathname_prefix = '/viz/asi/')
app.title = "Annual Survey of Industries"

# App layout
app.layout = html.Div(
    className="content-wrapper",
    children=[
        html.Div(
            style={'flex': '0 1 350px', 'padding': '10px', 'boxSizing': 'border-box',},
            children=[

                html.H1("Select Parameters to Get Chart!!!", className="parameter-data",style={'fontSize': '15px', 'fontWeight': 'normal','marginBottom': '0px', 'marginTop': '20px'}),

                html.Div(
                    children=[
                        html.Div(children="Indicator", className="menu-title"),
                        dcc.Dropdown(
                            id="indicator-dropdown",
                            options=[{'label': i, 'value': i} for i in df['indicator_description'].unique()],
                            clearable=False,
                            placeholder="Indicator",
                            searchable=False,
                            className="dropdown",
                            value="Number of Factories",style={"fontSize":"12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="State", className="menu-title"),
                        dcc.Dropdown(
                            id="state-dropdown",
                            options=[{'label': i, 'value': i} for i in df['state_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="State",
                            value="All India"
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="financial-year-container",
                    children=[
                        html.Div(children="Financial Year", className="menu-title"),
                        dcc.Dropdown(
                            id="financial-year-dropdown",
                             options=[{'label': 'Select All', 'value': 'Select All'}] + [{'label': str(year), 'value': year} for year in df['financial_year'].unique()],
                            multi=True,
                            className="dropdown",
                            placeholder="Select Financial Year",
                            value='Select All'
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Button(
                    'Apply', id='plot-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'text-align': 'center',
                        'text-decoration': 'none',
                        'display': 'inline-block',
                        'font-size': '16px',
                        'margin': '15px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginTop': '30px',
                        'marginBottom': '0px'
                    }
                ),
                html.Button(
                    'Download', id='download-svg-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'text-align': 'center',
                        'text-decoration': 'none',
                        'display': 'inline-block',
                        'font-size': '16px',
                        'margin': '20px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginBottom': '0px'
                    }
                ),
                dcc.Download(id="download-svg"),
                html.Div(
                    id='error-message',
                    style={'color': 'red', 'textAlign': 'center', 'marginTop': '20px'}
                ),
            ]
        ),
        html.Div(
            style={'flex': '1', 'padding': '20px', 'position': 'relative', 'text-align':'center'},
            children=[
                dcc.Loading(
                    id="loading-graph",
                    type="circle",color='#83b944',  # or "default"
                    children=[
                        html.Div(
                            id='graph-container',
                            #style={'width': '100%', 'height': '50vh'},
                            children=[
                                html.Div(
                                    className="loader",  # add a class for styling
                                    id="loading-circle",
                                    style={"position": "absolute", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"}
                                ),
                                dcc.Graph(
                                    id="time-series-plot",
                                    config={"displayModeBar": False},
                                    #style={'width': '100%', 'height': '80%'}
                                ),
                            ]
                        ),
                    ]
                ),
                # html.Div(
                #     id='info-text',
                #     style={'display': 'none', 'position': 'absolute', 'bottom': '40px', 'right': '10px', 'background-color': 'white', 'padding': '10px', 'border-radius': '5px', 'box-shadow': '0px 0px 5px 0px rgba(0,0,0,0.75)'},
                #     children=[
                #         html.P("This is a ASI Time Series Plot visualization. Select the parameters from the dropdowns on the left to generate the plot. You can also download the plot as an SVG image by clicking the 'Download' button."),
                #     ]
                # ),
                # html.Button(
                #     html.I(className="fas fa-info-circle"),
                #     id="info-button",
                #     className='info-button',
                #     style={
                #         'position': 'absolute',
                #         'bottom': '10px',
                #         'right': '10px',
                #         'background': 'none',
                #         'border': 'none',
                #         'color': 'black',
                #         'cursor': 'pointer',
                #         'font-size': '24px'
                #     }
                # ),
            ],
        ),
    ]
)

# Define callback to update plot and reset dropdowns and graph
@app.callback(
    [Output("time-series-plot", "figure"),
     Output('error-message', 'children'),
     Output('graph-container', 'style'),
     Output("indicator-dropdown", "value"),
     Output("state-dropdown", "value"),
     Output("financial-year-dropdown", "value")],
     #Output('info-text', 'style')],
    [Input('plot-button', 'n_clicks'),
     #Input('info-button', 'n_clicks'),
     Input('graph-container', 'n_clicks')],
    [
        State("indicator-dropdown", "value"),
        State("state-dropdown", "value"),
        State("financial-year-dropdown", "value"),
        #State('info-text', 'style')
    ]
)
def update_plot(n_clicks_plot, n_clicks_graph, selected_indicator, selected_state, selected_financial_years):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "plot-button":
        if n_clicks_plot == 0 or not (selected_indicator and selected_state):
            return dash.no_update, "", {'display': 'none'}, selected_indicator, selected_state, selected_financial_years

        if 'Select All' in selected_financial_years:
            filtered_df = df[
                (df['indicator_description'] == selected_indicator) &
                (df['state_description'] == selected_state)
            ]
        else:
            filtered_df = df[
                (df['indicator_description'] == selected_indicator) &
                (df['state_description'] == selected_state) &
                (df['financial_year'].isin(selected_financial_years))
            ]
        if not filtered_df.empty:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=filtered_df['financial_year'], y=filtered_df['indicator_value'],
                mode='lines+markers', line=dict(color='#0A3F63'), marker=dict(color='#0A3F63'),
                name='Indicator_value'
            ))

            #string = "Annual Survey of Industries"

            unit_description = df1[df1['description'] == selected_indicator]['unit'].iloc[0]
            # Replace '-' with 'Quantity' in unit description
            if unit_description == '-':
                unit_description = 'Quantity'

            fig.update_layout(
                # title={
                #     'text': f"<span style='text-decoration:underline;'>{string}</span>",
                #     'x': 0.5,
                #     'xanchor': 'center'
                # },
                xaxis_title='Financial Year',
                yaxis_title=f'{selected_indicator} ({unit_description})',  # Modified here
                template='plotly_white',
                title_font=dict(size=25, family='Arial, sans-serif', color='black', weight='bold'),
                xaxis_title_font=dict(size=18, family='Arial, sans-serif', color='black', weight='bold'),
                yaxis_title_font=dict(size=18, family='Arial, sans-serif', color='black', weight='bold'),
                font_color='black',
                margin=dict(t=0),
                # title_x=0.5,
                 width=None,  # Set width to None to allow Plotly to adjust dynamically
                height=None,  # Set height to None to allow Plotly to adjust dynamically
                autosize=True, 

            )

            fig.update_xaxes(type='category', color='black')
            fig.update_yaxes(color='black')

            return fig, "", {'display': 'block'}, selected_indicator, selected_state, selected_financial_years
        else:
            return dash.no_update, "This combination does not exist. Please try another combination.", {'display': 'none'}, selected_indicator, selected_state, selected_financial_years
    # elif button_id == "info-button":
    #     if info_style['display'] == 'none':
    #         info_style['display'] = 'block'
    #     else:
    #         info_style['display'] = 'none'
        #return dash.no_update, "", dash.no_update, selected_indicator, selected_state, selected_financial_years

    elif button_id == "graph-container":
        #info_style['display'] = 'none'
        return dash.no_update, "", dash.no_update, selected_indicator, selected_state, selected_financial_years

    else:
        if 'Select All' in selected_financial_years:
            filtered_df = df[
                (df['indicator_description'] == selected_indicator) &
                (df['state_description'] == selected_state)
            ]
        else:
            filtered_df = df[
                (df['indicator_description'] == selected_indicator) &
                (df['state_description'] == selected_state) &
                (df['financial_year'].isin(selected_financial_years))
            ]
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=filtered_df['financial_year'], y=filtered_df['indicator_value'],
            mode='lines+markers', line=dict(color='#0A3F63'), marker=dict(color='#0A3F63'),
            name='Indicator_value'
        ))

        #string = "Annual Survey of Industries"

        unit_description = df1[df1['description'] == selected_indicator]['unit'].iloc[0]
        # Replace '-' with 'Quantity' in unit description
        if unit_description == '-':
            unit_description = 'Quantity'

        fig.update_layout(
            # title={
            #     'text': f"<span style='text-decoration:underline;'>{string}</span>",
            #     'x': 0.5,
            #     'xanchor': 'center'
            # },
            xaxis_title='Financial Year',
            yaxis_title=f'{selected_indicator} ({unit_description})',  # Modified here
            template='plotly_white',
            title_font=dict(size=25, family='Arial, sans-serif', color='black', weight='bold'),
            xaxis_title_font=dict(size=18, family='Arial, sans-serif', color='black', weight='bold'),
            yaxis_title_font=dict(size=18, family='Arial, sans-serif', color='black', weight='bold'),
            font_color='black',
            margin=dict(t=0),
            # title_x=0.5,
            width=None,  # Set width to None to allow Plotly to adjust dynamically
            height=None,  # Set height to None to allow Plotly to adjust dynamically
            autosize=True, 
        )

        fig.update_xaxes(type='category', color='black')
        fig.update_yaxes(color='black')

        return fig, "", {'display': 'block'}, selected_indicator, selected_state, selected_financial_years

# Define callback to download SVG
@app.callback(
    Output("download-svg", "data"),
    Input("download-svg-button", "n_clicks"),
    State("time-series-plot", "figure"),
    prevent_initial_call=True
)
def download_svg(n_clicks, figure):
    if n_clicks > 0:
        # Create the SVG content
        fig = go.Figure(figure)
        svg_str = pio.to_image(fig, format="svg")

        # Create a BytesIO buffer and write the SVG string to it
        buffer = io.BytesIO()
        buffer.write(svg_str)
        buffer.seek(0)

        # Return the SVG data for download
        return dcc.send_bytes(buffer.getvalue(), "plot.svg")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,dev_tools_ui=False, dev_tools_props_check=False,host='0.0.0.0', port=9003)