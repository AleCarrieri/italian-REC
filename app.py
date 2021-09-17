import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_table

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import time

import base64
import io

import urllib.request
import urllib.parse
import json
from geopy.geocoders import Nominatim

from dash_extensions import Lottie

options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))

df_Res = pd.read_excel('Residential.xlsx')
df_Comm = pd.read_excel('Commercial.xlsx')
df_Ind = pd.read_excel('Industrial.xlsx')
df_HeatCool = pd.read_excel('HeatCool.xlsx')

# define colors
colDay= ('darkseagreen', 'indianred', 'darkorange', '#F0E442', 'lightslategrey', 'silver', 'steelblue')
cols= ('#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2','#F0E442')
colCarp= ('#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2')

# _____________________________________________________________________________________________________________________
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.YETI, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                suppress_callback_exceptions=True)
server = app.server
# app.title = "Energy Community"


def generate_modal_consumer():
    return html.Div(
        id="markdown_cons",
        className="modal",
        children=(
            html.Div(
                id="markdown-container_cons",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close_cons",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                        # User specification:
                        Answer few quick questions in order to evaluate your consumption and use an identifying name for each Load.

                    """
                            )
                        ),
                    ),
                    html.Br(),
                    dcc.Tabs(id="tabs_styled_with_props", value='Residential',
                             children=[
                                 dcc.Tab(
                                     label='Residential', value='Residential', className='custom-tab',
                                 ),
                                 dcc.Tab(label='Commercial', value='Commercial', className='custom-tab',
                                         ),
                                 dcc.Tab(label='Industrial', value='Industrial', className='custom-tab',
                                         ),
                             ],
                             parent_className='custom-tabs', className='custom-tabs-container'),
                    html.Div(id='tabs-content-props'),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Form(
                                [
                                    dbc.FormGroup(
                                        [
                                            dbc.Input(
                                                id='editing_columns_name',
                                                type='text',
                                                placeholder="Enter a name",
                                                bs_size="lg"),
                                        ],
                                        className="mr-3",
                                    ),
                                    dbc.Button("Add", color="primary", id='submit-button', size="lg", n_clicks=0),
                                ],
                                inline=True,
                            ),
                        ], width=12),
                    ], style={'height': 50}),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([
                            html.Button("Save Loads Excel", id="save-button_load", style={'color': 'white'}),
                            html.P(['']),
                            html.P(['▼'], style={'color': 'red'}),
                            html.P(['▼'], style={'color': 'red'}),
                            html.P(['▼'], style={'color': 'red'}),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col([]),
                        dbc.Col([
                            dcc.Upload(
                                id='LOADS-upload',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select your LOADS Data File')
                                ]),
                                style={
                                    'color': 'white',
                                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                    'borderWidth': '1px', 'borderStyle': 'dashed',
                                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                                    'background-color': 'orangered'
                                },
                            ),
                        ]),
                    ]),
                ],
            )
        ),
    )
def generate_modal_producer():
    return html.Div(
        id="markdown_prod",
        className="modal",
        children=(
            html.Div(
                id="markdown-container_prod",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close_prod",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                        # PV Plant specification:
                        Answer few quick questions in order to evaluate your PV production.

                    """
                            )
                        ),
                    ),
                    html.Br(),
                    html.Br(),
                    html.H3(["Cell type"], style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'white'}),
                    dbc.Row([
                        dbc.Col([
                        ], width=1),
                        dbc.Col([
                            html.Label(['Type:'], style={'font-weight': 'bold'}),
                            html.Br(),
                            dcc.Dropdown(
                                id='pvtechchoice',
                                options=[
                                    {'label': 'Crystalline silicon', 'value': 'crystSi'},
                                    {'label': 'CIS or CIGS thin-film modules', 'value': 'CIS'},
                                    {'label': 'CdTe thin film modules', 'value': 'CdTe'},
                                    {'label': 'Unknown', 'value': 'Unknown'},
                                ],
                                value='crystSi',
                            )
                        ], width=2),
                        dbc.Col([
                        ], width=2),
                        dbc.Col([
                            html.Label(
                                "System losses [%]:",
                                id="tooltip-target",
                                style={'font-weight': 'bold', "cursor": "pointer"},
                            ),
                            dbc.Tooltip(
                                "System losses include all losses in the system that reduce the energy returned to the electricity grid compared to the energy produced by the modules. There are various types of losses, such as resistive losses in the cables, losses in the inverter, dust or snow and so on. In addition, over time the modules tend to lose some power, and for this reason the average yield calculated for the entire life of the plant will be less than the yield in the first years."
                                ,
                                # "We suggest a default value for losses of 14%, including the aging effect. If you think you have lower losses (perhaps with a high efficiency inverter) you can reduce the system loss.",
                                target="tooltip-target",
                            ),
                            html.Br(),
                            daq.Slider(
                                id='loss',
                                min=0,
                                max=30,
                                dots=1,
                                value=14,
                                size=600,
                                handleLabel={"showCurrentValue": True, "label": " "},
                                step=1
                            )
                        ], width=7),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                    ], justify="end"),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Hr(),
                    html.H3(["Plant "], style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'white'}),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            html.Label(['Localization:'], style={'font-weight': 'bold'}),
                            dcc.RadioItems(
                                id='mountingplace',
                                options=[
                                    {'label': 'Free standing', 'value': 'free'},
                                    {'label': 'PV on roof', 'value': 'building'},
                                ],
                                value='building',
                                labelStyle={'display': 'block'}
                            )
                        ], width=6),
                        dbc.Col([
                            daq.LEDDisplay(
                                id='my-PV-display',
                                label="kW",
                                backgroundColor="seagreen",
                                size=64
                            ),
                            html.Label(['Nominal power of the PV system:'], style={'font-weight': 'bold'}),
                            html.Br(),
                            daq.NumericInput(
                                id='PV_POWER_numeric_input',
                                labelPosition='bottom',
                                value=3,
                                min=1,
                                max=199,
                            ),
                        ])
                    ]),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Form(
                                [
                                    dbc.FormGroup(
                                        [
                                            dbc.Input(
                                                id='editing_columns_name_prod',
                                                type='text',
                                                placeholder="Enter a name",
                                                bs_size="lg"),
                                        ],
                                        className="mr-3",
                                    ),
                                    dbc.Button("Add", color="primary", id='submit-button_prod',size="lg", n_clicks=0),
                                ],
                                inline=True,
                            ),
                        ], width=12),
                    ], style={'height': 50}),
                    html.Br(),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([
                            html.Button("Save PV Excel", id="save-button_prod", style={'color': 'white'}),
                            html.P(['']),
                            html.P(['▼'], style={'color': 'green'}),
                            html.P(['▼'], style={'color': 'green'}),
                            html.P(['▼'], style={'color': 'green'}),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col([]),
                        dbc.Col([
                            dcc.Upload(
                                id='PV-upload',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select your PV Plants Data File')
                                ]),
                                style={
                                    'color': 'white',
                                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                    'borderWidth': '1px', 'borderStyle': 'dashed',
                                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                                    'background-color': '#4CAF50'
                                },
                            ),
                        ]),
                    ]),
                ])
        ),
    )
def generate_modal_members():
    return html.Div(
        id="markdown_members",
        className="modal",
        children=(
            html.Div(
                id="markdown-container_members",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close_members",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                                # Energy Community Members Specification:
                                Define if the EC Member is a Consumer, a Producers or a Prosumers, then select its load/PV plant.
                    """
                            )
                        ),
                    ),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([]),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(Lottie(options=options, width="50%", height="50%",
                                                      url="assets/8823-user.json")),
                            ], color="#2d3038"),
                            html.Br(),
                            html.Br(),
                        ]),
                        dbc.Col([
                            html.Br(),
                            html.Br(),
                            dbc.RadioItems(
                                id="member_type",
                                options=[
                                    {"label": "Consumer", "value": "Consumer"},
                                    {"label": "Producer", "value": "Producer"},
                                    {"label": "Prosumer", "value": "Prosumer"},
                                ],
                                value="Consumer",
                                inline=True,
                            ),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(
                                    Lottie(id='ImageConsProdPros', options=options, width="100%", height="100%")),
                            ], color="#2d3038"),
                        ]),
                        dbc.Col([
                          html.Div(id='define_perc_prodcons'),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dash_table.DataTable(id='datatable_ECsummary2',
                                                 columns=[],
                                                 data=[],
                                                 style_table={'height': '455px',
                                                              'padding': '8px',
                                                              'textAlign': 'center',
                                                              'border-collapse': 'collapse',
                                                              'overflowY': 'auto',
                                                              # 'overflowX': 'auto',
                                                              'font-size': '16px',
                                                              'font-family': 'sans-serif',
                                                              'width': '100%'
                                                              },
                                                 style_cell={
                                                     'whiteSpace': 'normal',
                                                     'backgroundColor': '#f5f5f5',
                                                     'color': 'navy',
                                                     'text-align': 'center',
                                                     'border': '1px solid grey'
                                                 },
                                                 style_header={
                                                     'backgroundColor': 'cadetblue',
                                                     'fontWeight': 'bold',
                                                     'color': 'white'
                                                 },
                                                 )]),
                        dbc.Col([
                            html.Br(),
                            html.Br(),
                            html.Label(['Insert an unique User_ID:'], style={'font-weight': 'bold', 'color': 'white'}),
                            html.Br(),
                            dbc.Form(
                                [
                                    dbc.FormGroup(
                                        [
                                            dbc.Input(id='name', type='text',
                                                      placeholder="Enter a name",
                                                      bs_size="lg"),
                                        ],
                                        className="mr-3",
                                    ),
                                    dbc.Button("Add", color="info", id="add_members", size="lg", n_clicks=0),
                                ],
                                inline=True,
                            ),
                            html.Br(),
                            html.Br(),
                        ]),
                    ]),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            html.Button("Save EC Configuration", id="save_conf-button_EC", style={'color': 'white'}),
                            html.P(['']),
                            html.P(['▼'], style={'color': 'steelblue'}),
                            html.P(['▼'], style={'color': 'steelblue'}),
                            html.P(['▼'], style={'color': 'steelblue'}),
                        ]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([
                            html.Button("Save EC Data", id="save-button_EC", style={'color': 'white'}),
                            html.P(['']),
                            html.P(['▼'], style={'color': 'steelblue'}),
                            html.P(['▼'], style={'color': 'steelblue'}),
                            html.P(['▼'], style={'color': 'steelblue'}),
                        ]),
                    ],justify='center'),
                    dbc.Row([
                        dbc.Col([
                            dcc.Upload(
                                id='EC-conf-upload',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select your EC Summary Configuration File')
                                ]),
                                style={
                                    'color': 'white',
                                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                    'borderWidth': '1px', 'borderStyle': 'dashed',
                                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                                    'background-color': 'cadetblue'
                                },
                            ),
                        ]),
                        dbc.Col([
                            dcc.Upload(
                                id='EC-upload',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select your EC Data File')
                                ]),
                                style={
                                    'color': 'white',
                                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                    'borderWidth': '1px', 'borderStyle': 'dashed',
                                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                                    'background-color': 'cadetblue'
                                },
                            ),
                        ]),
                    ]),
                ],
            ),
        ),
    )

def callPVGIS_API(city,PV_POWER_numeric_input, loss, pvtechchoice, mountingplace, editing_columns_name_prod):
    City = "{}".format(city)
    lat = Nominatim(user_agent="my_user_agent").geocode(City + ',' + "Italy").latitude
    lon = Nominatim(user_agent="my_user_agent").geocode(City + ',' + "Italy").longitude
    df_PVGIS = pd.DataFrame(
        json.loads(urllib.request.urlopen("https://re.jrc.ec.europa.eu/api/seriescalc" + "?" + urllib.parse.urlencode(
            {
                "lat": lat,
                "lon": lon,
                "peakpower": PV_POWER_numeric_input,
                "pvtechchoice": pvtechchoice,
                "raddatabase": "PVGIS-SARAH",
                "startyear": "2013",
                "endyear": "2013",
                "mountingplace": mountingplace,
                "pvcalculation": "1",
                "loss": loss,
                "optimalinclination": "1",
                "optimalangles": "1",
                "outputformat": "json"}
        )).read().decode("utf-8"))["outputs"]["hourly"])
    df_PVGIS.drop(['G(i)', 'H_sun', 'T2m', 'WS10m', 'Int', 'Year'], inplace=True, axis=1, errors='ignore')
    df_PVGIS['time'] = pd.to_datetime(df_PVGIS['time'], format='%Y%m%d:%H%M')
    df_PVGIS[editing_columns_name_prod] = df_PVGIS['P'] / 1000
    df_PVGIS.drop(['P'], inplace=True, axis=1, errors='ignore')
    return df_PVGIS.round(decimals=2)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "280px",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
# the styles for the main content position it to the right of the sidebar and add some padding.
sidebar = html.Div(
    [
        html.Div(
            html.Img(src=app.get_asset_url('Logo_PoliTo_dal_2021_blu.png'), style={'height': '100%', 'width': '100%'})),
        html.Hr(),
        html.H2(["Energy Community"],
                style={'textAlign': 'center', 'font-style': 'italic', 'font-weight': 'bold', 'color': 'navy'}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("                                                           Setup", href="/", active="exact", className="fas fa-users-cog"),
                dbc.NavLink("                                                           Yearly energy data and benefits", href="/page-1", active="exact", className="fas fa-chart-line"),
                dbc.NavLink("                                                           Economics", href="/page-2", active="exact", className="fas fa-euro-sign"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
    ], style=SIDEBAR_STYLE)

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
content = html.Div(id="page-content",
                   style=CONTENT_STYLE)


app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar, content,
    dcc.Download(id="download_df_load"),
    dcc.Download(id="download_df_prod"),
    dcc.Download(id="download_df_EC"),
    dcc.Download(id="download_df_conf_EC"),
    html.Br(),
    dcc.Store(id='EC_Data', storage_type='memory'),
    dcc.Store(id='LOADScontainer_data', storage_type='memory'),
    dcc.Store(id='PVcontainer_data', storage_type='memory'),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(id='datatable_conf_ECsummary',
                                 columns=[],
                                 data=[],
                                 page_action='none',
                                 style_table={'height': '455px',
                                              'padding': '8px',
                                              'textAlign': 'center',
                                              'border-collapse': 'collapse',
                                              'overflowY': 'auto',
                                              # 'overflowX': 'auto',
                                              'font-size': '16px',
                                              'font-family': 'sans-serif',
                                              'width': '100%'
                                              },
                                 style_cell={
                                     'whiteSpace': 'normal',
                                     'backgroundColor': '#f5f5f5',
                                     'color': 'navy',
                                     'text-align': 'center',
                                     'border': '1px solid grey'
                                 },
                                 fill_width=False,
                                 style_header={
                                     'backgroundColor': 'cadetblue',
                                     'fontWeight': 'bold',
                                     'color': 'white'
                                 },
                                 ),
        ],width=6),
        dbc.Col([
            dash_table.DataTable(id='datatable_cons-summary',
                                 columns=[],
                                 data=[],
                                 page_action='none',
                                 style_table={'height': '455px',
                                              'padding': '8px',
                                              'textAlign': 'center',
                                              'border-collapse': 'collapse',
                                              'overflowY': 'auto',
                                              # 'overflowX': 'auto',
                                              'font-size': '16px',
                                              'font-family': 'sans-serif',
                                              'width': '100%'
                                              },
                                 style_cell={
                                     'whiteSpace': 'normal',
                                     'backgroundColor': '#f5f5f5',
                                     'color': 'navy',
                                     'text-align': 'center',
                                     'border': '1px solid grey'
                                 },
                                 fill_width=False,
                                 style_header={
                                     'backgroundColor': 'orangered',
                                     'fontWeight': 'bold',
                                     'color': 'white'
                                 },
                                 ),
        ],width=3),
        dbc.Col([
            dash_table.DataTable(id='datatable_prod-summary',
                                 columns=[],
                                 data=[],
                                 page_action='none',
                                 style_table={'height': '455px',
                                              'padding': '8px',
                                              'textAlign': 'center',
                                              'border-collapse': 'collapse',
                                              'overflowY': 'auto',
                                              # 'overflowX': 'auto',
                                              'font-size': '16px',
                                              'font-family': 'sans-serif',
                                              'width': '100%'
                                              },
                                 style_cell={
                                     'whiteSpace': 'normal',
                                     'backgroundColor': '#f5f5f5',
                                     'color': 'navy',
                                     'text-align': 'center',
                                     'border': '1px solid grey'
                                 },
                                 fill_width=False,
                                 style_header={
                                     'backgroundColor': '#4CAF50',
                                     'fontWeight': 'bold',
                                     'color': 'white'
                                 },
                                 ),
        ],width=3),
    ], justify="center"),
    html.Br(),
    html.Br(),
])

# callback for Sidebar:define what's in the App
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def render_page_content(pathname):
    if pathname == "/":
        return dbc.Container([
            html.Div([
                dbc.Jumbotron(
                    [
                        html.H1(["Energy Community Setup"], style={'color': 'white', 'textAlign': 'center'},
                                className="display-3"),
                        html.Hr(className="my-2"),
                        html.P(["Enter your city, than define the electrical Loads and PV Plants in your Energy Community."
                                ],
                               style={'color': 'white', 'textAlign': 'center'},
                               className="lead"),
                        html.P(
                            ["Define REC members by associating their respective load and PV Plant."],
                            style={'color': 'white', 'textAlign': 'center'},
                            className="lead"),
                        html.P(["By uploading your data, the Energy Community Setup will be completed."],
                               style={'color': 'white', 'textAlign': 'center'},
                               className="lead"),
                    ]
                    , style={'background-image': 'url(assets/MicrosoftTeams-image1.jpg)',
                             'background-repeat': 'no-repeat', 'background-size': 'cover'}),
                dbc.Row([
                    dbc.Col([
                        html.Iframe(src="https://www.youtube.com/embed/BFHocTGimMc",style={"height": "100%", "width": "100%", 'background-color': 'white' }),
                    ]),
                    dbc.Col([
                        dbc.CardHeader(
                            Lottie(url="assets/Localization.json", options=options, width="80%", height="80%")),
                        html.Br(),
                        dbc.Form(
                            [
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Localization", className="mr-4",
                                                  style={"color": "navy", "font-weight": "bold"},
                                                ),
                                        dbc.Input(id='city', value='Torino', type='text',
                                                  placeholder="Enter your city",
                                                  bs_size="lg")
                                    ],
                                    className="mr-4",
                                ),
                            ],
                            inline=True,
                        ),
                    ],lg='auto', width='auto'),
                ], justify="end"),
                html.Br(),
                html.Br(),
                html.Hr(),
                html.Br(),
                dbc.Row([
                    dbc.Col(),
                    dbc.Col([
                        html.Button('LOADS', id='collapse-buttonLOADSsetup', n_clicks=0,
                                    style={'background-color': 'orangered', 'color': 'white', 'width': '100%',
                                           'height': '100%', 'textAlign': 'center'}),
                    ]),
                    dbc.Col([
                        html.Button('PV Plants', id='collapse-buttonPVsetup', n_clicks=0,
                                    style={'background-color': '#4CAF50', 'color': 'white', 'width': '100%',
                                           'height': '100%', 'textAlign': 'center'}),
                    ]),
                    dbc.Col([
                        html.Button('Members', id='collapse-buttonMEMBERSsetup', n_clicks=0,
                                         style={'background-color': 'cadetblue', 'color': 'white', 'width': '100%',
                                                'height': '100%', 'textAlign': 'center'})]),
                    dbc.Col(),
                ], justify='center'),
                dbc.Collapse([
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(Lottie(options=options, width="100%", height="100%",
                                                      url="assets/59927-buzzing-round-button.json")),
                                dbc.CardBody([
                                    html.Button('Add Load', id='learn-more-button_cons', n_clicks=0,
                                                style={'background-color': 'orangered', 'color': 'white',
                                                       'width': '100%', 'height': '80%', 'textAlign': 'center'}),
                                ])
                            ], color="light", style={"width": "18rem"}),
                        ]),
                        dbc.Col([
                            dash_table.DataTable(
                                id='adding-rows-table',
                                columns=[],
                                data=[],
                                page_action='none',
                                style_table={'height': '455px',
                                             'padding': '8px',
                                             'overflowY': 'auto',
                                             'text-align': 'center',
                                             'border-collapse': 'collapse',
                                             'font-size': '16px',
                                             'font-family': 'sans-serif',
                                             'width': '50%'
                                             },
                                style_cell={
                                    'backgroundColor': '#f5f5f5',
                                    'color': 'navy',
                                    'text-align': 'center',
                                    'border-bottom': '2px solid  # ddd',
                                },
                                style_header={
                                    'backgroundColor': '#CA0B00',
                                    'fontWeight': 'bold',
                                    'text-align': 'center',
                                    'color': 'white'
                                },
                                row_deletable=True,
                                editable=True,
                                export_format='xlsx',
                            ),
                        ]),
                        dbc.Col([
                            dash_table.DataTable(
                                id='editing_columns_cons',
                                columns=[],
                                data=[],
                                style_table={'height': '455px', 'overflowY': 'auto', 'display': 'block'},
                                style_cell={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'color': 'navy',
                                    'border': '1px solid grey'
                                },
                                style_header={
                                    'backgroundColor': '#CA0B00',
                                    'fontWeight': 'bold',
                                    'color': 'white'
                                },
                            ),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col([
                        ]),
                        dbc.Col([
                            dcc.Upload(
                                id='cons-summary-upload',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select your LOADS Summary File')
                                ]),
                                style={
                                    'color': 'white',
                                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                    'borderWidth': '1px', 'borderStyle': 'dashed',
                                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                                    'background-color': 'coral'
                                },
                            ),
                        ]),
                        dbc.Col([
                        ]),
                    ]),
                    html.Br(),
                    dcc.Loading(
                        id="loading-1",
                        type='cube',
                        color='navy',
                        fullscreen=True,
                        children=html.Div(id="loading-output-1", style={'color': 'navy'})
                    ),
                    html.Hr(),
                    html.Hr(),
                ],
                    id="collapse_LOADSsetup",
                    is_open=False),
                dbc.Collapse([
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(
                                    Lottie(options=options, width='100%', height='100%', url="assets/PV.json")),
                                dbc.CardBody([
                                    html.Button('Add PV Plant', id='learn-more-button_prod', n_clicks=0,
                                                style={'background-color': '#4CAF50', 'color': 'white', 'width': '100%',
                                                       'height': '80%', 'textAlign': 'center'}),
                                ])
                            ], color="light", style={"width": "18rem"}, ),
                        ]),
                        dbc.Col([
                            dash_table.DataTable(
                                id='adding-rows-table_prod',
                                columns=[],
                                data=[],
                                page_action='none',
                                style_table={'height': '455px',
                                             'padding': '8px',
                                             'overflowY': 'auto',
                                             'text-align': 'center',
                                             'border-collapse': 'collapse',
                                             'font-size': '16px',
                                             'font-family': 'sans-serif',
                                             'width': '50%'
                                             },
                                style_cell={
                                    'backgroundColor': '#f5f5f5',
                                    'color': 'navy',
                                    'text-align': 'center',
                                    'border-bottom': '2px solid  # ddd',
                                },
                                style_header={
                                    'backgroundColor': 'steelblue',
                                    'fontWeight': 'bold',
                                    'text-align': 'center',
                                    'color': 'white'
                                },
                                row_deletable=True,
                                editable=True,
                                export_format='xlsx',
                            ),
                        ]),
                        dbc.Col([
                            dash_table.DataTable(
                                id='editing-columns_prod',
                                data=[],
                                columns=[],
                                style_table={'height': '455px', 'overflowY': 'auto', 'display': 'block'},
                                style_cell={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'color': 'navy',
                                    'border': '1px solid grey'
                                },
                                style_header={
                                    'backgroundColor': 'steelblue',
                                    'fontWeight': 'bold',
                                    'color': 'white'
                                },
                            ),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col([
                        ]),
                        dbc.Col([
                            dcc.Upload(
                                id='prod-summary-upload',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select your PV Summary File')
                                ]),
                                style={
                                    'color': 'white',
                                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                    'borderWidth': '1px', 'borderStyle': 'dashed',
                                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                                    'background-color': 'darkseagreen'
                                },
                            ),
                        ]),
                        dbc.Col([
                        ]),
                    ]),
                    html.Br(),
                    dcc.Loading(
                        id="loading-2",
                        type='cube',
                        color='navy',
                        fullscreen=True,
                        children=html.Div(id="loading-output-2", style={'color': 'navy'})
                    ),
                    html.Hr(),
                    html.Hr(),

                ],
                    id="collapse_PVsetup",
                    is_open=False),
                dbc.Collapse([
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dash_table.DataTable(
                                id='editing_columns_members',
                                columns=[],
                                data=[],
                                style_table={'height': '455px', 'overflowY': 'auto', 'display': 'block'},
                                style_cell={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'color': 'navy',
                                    'border': '1px solid grey'
                                },
                                style_header={
                                    'backgroundColor': 'navy',
                                    'fontWeight': 'bold',
                                    'color': 'white'
                                },
                            ),
                        ]),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(Lottie(options=options, width="100%", height="100%",
                                                      url="assets/5166-users-icons.json")),
                                dbc.CardBody([
                                    html.Button('Define Members', id='learn_more_button_members', n_clicks=0,
                                                style={'background-color': 'cadetblue', 'color': 'white',
                                                       'width': '100%',
                                                       'height': '100%', 'textAlign': 'center', 'margin': 'auto'}),
                                ])
                            ], color="light"),
                        ], lg='auto', width='auto'),
                    ], justify='center'),
                    dcc.Loading(
                        id="loading-3",
                        type='cube',
                        color='navy',
                        fullscreen=True,
                        children=html.Div(id="loading-output-3", style={'color': 'navy'})
                    ),

                ],
                    id="collapse_MEMBERSdefinition",
                    is_open=False),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.CardHeader(
                            Lottie(options=options, width="50%", height="50%", url="assets/13893-eco-living.json"))
                    ]),
                ], justify="center"),
                ]),
            generate_modal_consumer(),
            generate_modal_producer(),
            generate_modal_members(),
        ], fluid=True)
    elif pathname == "/page-1":
          return dbc.Container([
            html.Div([dbc.Jumbotron(
                [
                    html.H1(["Visual representation of Consumption & Production data"], style={'color': 'white', 'textAlign': 'center'}, className="display-3"),
                    html.P(["Extract knowledge from energy data"], style={'color': 'white', 'textAlign': 'center'}, className="lead"),
                    html.Hr(className="my-2"),
                    html.P(["Discover the annual benefits at community level and at member level."],
                           style={'color': 'white', 'textAlign': 'center'},
                           className="lead"),
                ]
                , style={'background-image': 'url(assets/MicrosoftTeams-image1.jpg)', 'background-repeat': 'no-repeat',
                         'background-size': 'cover'})]),
              html.Br(),
              html.Br(),
              dcc.Loading(
                  id="loading-4",
                  type='graph',
                  color='navy',
                  fullscreen=True,
                  children=html.Div(id="loading-output-4", style={'color': 'navy'})
              ),
              html.Br(),
              html.Br(),
              dcc.Tabs(
                  id="tabs-historical_data",
                  value='tab-1',
                  parent_className='custom-tabs',
                  className='custom-tabs-container',
                  children=[
                      dcc.Tab(
                          label='Energy Community',
                          value='tab-1',
                          className='custom-tab',
                          selected_className='custom-tab--selected'
                      ),
                      dcc.Tab(
                          label='Members',
                          value='tab-2',
                          className='custom-tab',
                          selected_className='custom-tab--selected'
                      ),
                  ]),
              html.Br(),
              html.Div(id='tabs-content-historical_data'),
            ], fluid=True)
    elif pathname == "/page-2":
          return dbc.Container([
            html.Div([dbc.Jumbotron(
                [
                    html.H1(["Economics"], style={'color': 'white', 'textAlign': 'center'}, className="display-3"),
                    html.P(["GSE  incentives"], style={'color': 'white', 'textAlign': 'center'}, className="lead"),
                    html.Hr(className="my-2"),
                    html.P(["Evaluation of the investments  over a period of 20 years"],
                           style={'color': 'white', 'textAlign': 'center'},
                           className="lead"),
                ]
                , style={'background-image': 'url(assets/MicrosoftTeams-image1.jpg)', 'background-repeat': 'no-repeat',
                         'background-size': 'cover'})]),
              dbc.Row([
                  dbc.Col(dcc.Graph(id='graph_DonutCommunity2'), width=12),
              ]),
              html.Br(),
              dbc.Row([
                  dbc.Col([
                  ]),
                  dbc.Col([

                      dbc.Card([
                          dbc.CardHeader(Lottie(options=options, width="50%", height="50%",
                                                url="assets/8823-user.json")),
                      ], color="white"),
                      html.Br(),
                      dcc.Dropdown(
                          id='dropdown_member',
                          placeholder="Select a Member",
                      ),
                  ]),
                  dbc.Col([]),
              ], justify='center'),
              html.Br(),
              html.Br(),
              html.Br(),
              html.Br(),
              html.Br(),
              html.Br(),
              dbc.Row([
                  dbc.Col([dcc.Graph(id='economics_graph')], width=12),
              ]),
              html.Br(),
              html.Br(),
              dbc.Row([
                  html.H3(["GSE incentive distribution percentage % to PV Plants owners"],
                          style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'navy'}),
                  html.Br(),
                  html.Br(),
                  html.Br(),
              ], justify='center'),
              dcc.Slider(
                  id="slider_circular_incentive", min=1, max=100,
                  marks={
                      1: '1%',
                      10: '10%',
                      20: '20%',
                      30: '30%',
                      40: '40%',
                      50: '50%',
                      60: '60%',
                      70: '70%',
                      80: '80%',
                      90: '90%',
                      100: '100%',
                  },
                  value=80
              ),
              html.Br(),
              html.Br(),
              dbc.Row([
                  dcc.Input(id="input_circular_incentive", type="number", min=1, max=100, value=80,
                            placeholder="% GSE incentive"),
              ], justify='center'),
              html.Br(),
              html.Br(),
              html.Div([
                  html.P("Legend position"),
                  dcc.RadioItems(
                      id='yanchor',
                      options=[{'label': 'top', 'value': 1},
                               {'label': 'bottom', 'value': 0}],
                      value=1,
                      labelStyle={'color': 'navy'}
                  ),
                  html.Br(),
                  html.Br(),
                  dcc.RadioItems(
                      id='xanchor',
                      options=[{'label': 'left', 'value': 0},
                               {'label': 'right', 'value': 1}],
                      value=0,
                      labelStyle={'display': 'inline-block', 'color': 'navy'}
                  ),
              ], style={'color': 'navy'}),
          ], fluid=True)
# If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )
# _______________________________________________________________________________
# callback to Upload csv/excel file and pass data to DataTable (LOADS)
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))

@app.callback(Output('LOADScontainer_data', 'data'),
              Output('LOADScontainer_data', 'columns'),
              Input('LOADS-upload', 'contents'),
              State('LOADS-upload', 'filename'),
              )
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    del df['Unnamed: 0']
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]

# _________________________________________________________________________________________
# callback to  pass columns name to DropDown menus (LOADS)
@app.callback(Output('dropdown_members_cons', 'options'),
              [Input('LOADScontainer_data', 'data')],
              )
def update_output(rows):
    df=pd.DataFrame(rows)
    return [{'label': i, 'value': i} for i in df.columns]

# callback to  pass columns name to DropDown menus (LOADS)
@app.callback(Output('User_ID', 'options'),
              Output('User', 'options'),
              Output('User_ID', 'value'),
              Output('User', 'value'),
              [Input('EC_Data', 'data')],
              )
def update_output(rows):
    df_members = pd.DataFrame(rows)
    df_consumption = df_members.filter(regex='Consumption')
    df_consumption = df_consumption.loc[:, (df_consumption != 0).any(axis=0)]
    value1 = df_consumption.columns[0],
    value2 = df_consumption.columns[0]
    return [{'label': i, 'value': i} for i in df_consumption.columns], [{'label': i, 'value': i} for i in df_consumption.columns], value1, value2


# callback to pass all EC MEMBERS name to Dropdown menu
@app.callback(Output('dropdown_member', 'options'),
              Output('dropdown_member', 'value'),
              [Input('datatable_conf_ECsummary', 'data')]
)
def update_output(rows):
    df=pd.DataFrame(rows)
    value = df['User_ID'][0]
    return [{'label': i, 'value': i} for i in df['User_ID']], value


# callback to see member benefits (LOADS)
@app.callback(
    Output('EC_Consumption_member_LED','value'),
    Output('RealSelf_member_LED','value'),
    Output('fromgrid_member_LED', 'value'),
    Output('Energy_expenditure_member_LED', 'value'),
    Output('Savings_member_LED', 'value'),
    Output('GSE_Incentive_member1_LED', 'value'),
    [Input('EC_Data', 'data'),
     Input('User', 'value'),
     Input('input_circular_incentive2', 'value'),
     ])
def update_values(rows, User, value):
    df_members = pd.DataFrame(rows)
    Member = User.replace(' Consumption', '')

    df_member = df_members.filter(regex=Member)
    df_member.insert(loc=3,
                     column=' Energy withdrawn from the grid',
                     value=df_member[Member + ' Consumption'] - df_member[Member + ' Real Self Cons']),
    Cons = round((df_member[Member + ' Consumption'].sum() / 1000), 2)
    Energy_SelfCons = round((df_member[Member+' Real Self Cons'].sum() / 1000), 2)
    Energy_fromthegrid = round((df_member[' Energy withdrawn from the grid'].sum() / 1000), 2)
    Energy_expenditure = round((Energy_fromthegrid * 150), 2)
    Savings=round((Energy_SelfCons* 150),2)


    df_comm = pd.DataFrame(rows)
    df_cons = df_comm.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    cons = pd.unique(list(next(zip(*map(str.split, list(df_cons))))))
    # calcolo il totale dei vari utenti (sommo le colonne) ottengo colonna TOT 8760 valori
    df_cons['EC Consumption [kW]'] = df_cons.iloc[:, 0:(len(df_cons.columns))].sum(axis=1)
    users = pd.unique(list(next(zip(*map(str.split, list(df_comm))))))
    for user in users:
        df_comm.insert(loc=0,
                       column=user + ' Energy withdrawn from the grid',
                       value=df_comm[user + ' Consumption'] - df_comm[user + ' Real Self Cons'])
        df_comm.insert(loc=0,
                       column=user + ' Energy fed into the grid',
                       value=df_comm[user + ' Production'] - df_comm[user + ' Real Self Cons'])

    df_withdrawn_from = df_comm.filter(regex='withdrawn from')
    # get the total column in df_members Energy withdrawn from the grid
    df_comm['Energy withdrawn from the grid'] = df_withdrawn_from.iloc[:, 0:(len(df_withdrawn_from.columns))].sum(
        axis=1)

    df_fed_into = df_comm.filter(regex='fed into')
    # get the total column in df_members Energy fed into the grid
    df_comm['Energy fed into the grid'] = df_fed_into.iloc[:, 0:(len(df_fed_into.columns))].sum(axis=1)

    df_comm['Shared electricity [kW]'] = df_comm[['Energy fed into the grid', 'Energy withdrawn from the grid']].min(
        axis=1)
    df_comm['GSEIncEUR'] = df_comm['Shared electricity [kW]'] * 0.11822

    df_cons['GSEIncEUR Cons'] = df_comm['GSEIncEUR'] * (100-value)/100
    for user in cons:
        df_cons.insert(loc=0,
                       column=user + ' GSE Incentive',
                       value=(df_cons[user + ' Consumption'] * df_cons['GSEIncEUR Cons']) / df_cons[
                           'EC Consumption [kW]'])


    GSE_Incentive = round((df_cons[Member + ' GSE Incentive'].sum()), 2)

    return Cons, Energy_SelfCons, Energy_fromthegrid, Energy_expenditure, Savings, GSE_Incentive

# callback to see member benefits (Prod)
@app.callback(
    Output('EC_Production_member_LED','value'),
    Output('ingrid_member_LED','value'),
    Output('SaleEnergy_member_LED', 'value'),
    Output('GSE_Incentive_member2_LED', 'value'),
    [Input('EC_Data', 'data'),
     Input('Prod', 'value'),
     Input('input_circular_incentive2', 'value'),
     ])
def update_values(rows, Prod, value):
    df_members = pd.DataFrame(rows)
    Member = Prod.replace(' Production', '')
    df_member = df_members.filter(regex=Member)

    df_member.insert(loc=3,
                      column=' Energy fed into the grid',
                      value=df_member[Member + ' Production'] - df_member[Member + ' Real Self Cons'])

    Prod = round((df_member[Member + ' Production'].sum() / 1000), 2)
    Energy_intothegrid = round((df_member[' Energy fed into the grid'].sum() / 1000), 2)
    SaleEnergy = round((Energy_intothegrid * 50.1), 2)




    df_comm = pd.DataFrame(rows)
    df_prod = df_comm.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    prod = pd.unique(list(next(zip(*map(str.split, list(df_prod))))))
    # calcolo il totale dei vari utenti (sommo le colonne) ottengo colonna TOT 8760 valori
    df_prod['EC Production [kW]'] = df_prod.iloc[:, 0:(len(df_prod.columns))].sum(axis=1)

    users = pd.unique(list(next(zip(*map(str.split, list(df_comm))))))
    for user in users:
        df_comm.insert(loc=0,
                       column=user + ' Energy withdrawn from the grid',
                       value=df_comm[user + ' Consumption'] - df_comm[user + ' Real Self Cons'])
        df_comm.insert(loc=0,
                       column=user + ' Energy fed into the grid',
                       value=df_comm[user + ' Production'] - df_comm[user + ' Real Self Cons'])

    df_withdrawn_from = df_comm.filter(regex='withdrawn from')
    # get the total column in df_members Energy withdrawn from the grid
    df_comm['Energy withdrawn from the grid'] = df_withdrawn_from.iloc[:, 0:(len(df_withdrawn_from.columns))].sum(
        axis=1)

    df_fed_into = df_comm.filter(regex='fed into')
    # get the total column in df_members Energy fed into the grid
    df_comm['Energy fed into the grid'] = df_fed_into.iloc[:, 0:(len(df_fed_into.columns))].sum(axis=1)

    df_comm['Shared electricity [kW]'] = df_comm[['Energy fed into the grid', 'Energy withdrawn from the grid']].min(
        axis=1)
    df_comm['GSEIncEUR'] = df_comm['Shared electricity [kW]'] * 0.11822
    df_prod['GSEIncEUR Prod'] = df_comm['GSEIncEUR'] * value/100
    for user in prod:
        df_prod.insert(loc=0,
                       column=user + ' GSE Incentive',
                       value=(df_prod[user + ' Production'] * df_prod['GSEIncEUR Prod']) / df_prod[
                           'EC Production [kW]'])

    GSE_Incentive = round((df_prod[Member + ' GSE Incentive'].sum()), 2)
    return Prod, Energy_intothegrid, SaleEnergy, GSE_Incentive


#________________________________________________________________________________________
# callback to Upload csv/excel file and pass data to DataTable (PV Production)
@app.callback(Output('PVcontainer_data', 'data'),
              Output('PVcontainer_data', 'columns'),
              Input('PV-upload', 'contents'),
              State('PV-upload', 'filename'))
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    del df['Unnamed: 0']
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
# ______________________________________________________________________________________________________________________
# callback to  pass columns name to DropDown menus (PV)
@app.callback(Output('dropdown_members_prod', 'options'),
              Input('PVcontainer_data', 'data'),
              )
def update_output(rows):
    df=pd.DataFrame(rows)
    return [{'label': i, 'value': i} for i in df.columns]


# callback to  pass columns name to DropDown menus (PV Production)
@app.callback(Output('Prod_ID', 'options'),
              Output('Prod', 'options'),
              Output('Prod_ID', 'value'),
              Output('Prod', 'value'),
              Input('EC_Data', 'data'),
              )
def update_output(rows):
    df_members = pd.DataFrame(rows)
    df_production = df_members.filter(regex='Production')
    df_production = df_production.loc[:, (df_production != 0).any(axis=0)]
    value1 = df_production.columns[0],
    value2 = df_production.columns[0]
    return [{'label': i, 'value': i} for i in df_production.columns], [{'label': i, 'value': i} for i in df_production.columns], value1, value2



# # callback to Upload csv/excel file and pass data to DataTable (MEMBERS)
@app.callback(Output('EC_Data', 'data'),
              Output('EC_Data', 'columns'),
              Input('EC-upload', 'contents'),
              State('EC-upload', 'filename'))
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    del df['Unnamed: 0']
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]


# callback to Upload csv/excel file and pass data to summary DataTable (MEMBERS)
@app.callback(Output('datatable_conf_ECsummary', 'data'),
              Output('datatable_conf_ECsummary', 'columns'),
              Input('EC-conf-upload', 'contents'),
              State('EC-conf-upload', 'filename'))
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    del df['Unnamed: 0']
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]



# callback to Upload csv/excel file and pass data to summary DataTable (LOADS)
@app.callback(Output('datatable_cons-summary', 'data'),
              Output('datatable_cons-summary', 'columns'),
              Input('cons-summary-upload', 'contents'),
              State('cons-summary-upload', 'filename'))
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]


# callback to Upload csv/excel file and pass data to summary DataTable (PV)
@app.callback(Output('datatable_prod-summary', 'data'),
              Output('datatable_prod-summary', 'columns'),
              Input('prod-summary-upload', 'contents'),
              State('prod-summary-upload', 'filename'))
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]





# _________________________________________________________________________

@app.callback(Output("loading-output-1", "children"),
              Input('LOADS-upload', 'contents'))
def input_triggers_spinner(contents):
    if contents is None:
        return []
    else:
        time.sleep(1)
        message= dbc.Toast(
            [html.P("Your loads file has been uploaded successfully", className="mb-0")],
            id="simple-toast",
            header="Successful upload",
            icon="info",
            dismissable=True,
        )
        return message

@app.callback(Output("loading-output-2", "children"),
              Input('PV-upload', 'contents'))
def input_triggers_spinner(contents):
    if contents is None:
        return []
    else:
        time.sleep(1)
        message= dbc.Toast(
            [html.P("Your PV file has been uploaded successfully", className="mb-0")],
            id="simple-toast",
            header="Successful upload",
            icon="info",
            dismissable=True,
        )
        return message

@app.callback(Output("loading-output-3", "children"),
              Input('EC-upload', 'contents'))
def input_triggers_spinner(contents):
    if contents is None:
        return []
    else:
        time.sleep(1)
        message= dbc.Toast(
            [html.P("Your EC configuration file has been uploaded successfully", className="mb-0")],
            id="simple-toast",
            header="Successful upload",
            icon="info",
            dismissable=True,
        )
        return message



# ______________________________________________________________________________________________________________________
# ======= Callbacks for modal Popup LOADS=======
@app.callback(
    Output("markdown_cons", "style"),
    [Input("learn-more-button_cons", "n_clicks"),
     Input("markdown_close_cons", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button_cons":
            return {"display": "block"}
    return {"display": "none"}


# callback in Add LOAD Markdown (content)
@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs_styled_with_props', 'value'))
def render_content(tab):
    if tab == 'Residential':
        return html.Div([
            html.Br(),
            html.Br(),
            html.H3(["Building"], style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'white'}),
            dbc.Row([
                dbc.Col([
                    daq.LEDDisplay(
                        id='LED-display-Res',
                        label="Area [\u33A1]",
                        backgroundColor="#FF5E5E",
                        value=98,
                        size=100
                    ),
                    html.Br(),
                    dcc.Slider(
                        id='value_Area_Res',
                        dots=1,
                        min=10,
                        max=300,
                        step=10,
                        value=98,
                    ),
                ]),
            ]),
            html.Br(),
            html.Br(),
            html.Hr(),
            html.H3(["Occupant"], style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'white'}),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Label(['Number of people:'], style={'font-weight': 'bold'}),
                    html.Br(),
                    daq.NumericInput(
                        id='npeople_numeric_input',
                        labelPosition='bottom',
                        value=3,
                        min=1,
                        max=10,
                    ),
                ], width=3),
                dbc.Col([
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    dcc.Dropdown(
                        id='menu_res',
                        )
                ]),
            ]),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Hr(),
            html.H3(["Appliances"], style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'white'}),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    daq.BooleanSwitch(
                        id='aircond_boolean_switch',
                        on=False,
                        vertical=True,
                        label="Air conditioner",
                        labelPosition="top",
                        color="yellow",
                    )
                ], width=2),
                dbc.Col([
                    daq.BooleanSwitch(
                        id='dw_boolean_switch',
                        on=False,
                        vertical=True,
                        label="Dishwasher",
                        labelPosition="top",
                        color="yellow",
                    )
                ], width=2),

                dbc.Col([
                    daq.BooleanSwitch(
                        id='HP_boolean_switch',
                        on=False,
                        vertical=True,
                        label="Heat Pump",
                        labelPosition="top",
                        color="yellow",
                    )
                ], width=2),
            ], justify='center'),
            dcc.Dropdown(
                id='menu_comm',
                disabled=True,
                style={'display': 'none'}
            ),
            dcc.Dropdown(
                id='menu_ind',
                disabled=True,
                style={'display': 'none'}
            ),
        ])
    elif tab == 'Commercial':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Label(['Type of activity:'], style={'font-weight': 'bold'}),
                    html.Br(),
                    dcc.Dropdown(
                        id='menu_comm',
                        options=[
                            {'label': 'Office', 'value': 'Office'},
                            {'label': 'Shop Weekdays 8-18', 'value': 'Shop Weekdays 8-18'},
                            {'label': 'Shop Weekdays 8-22', 'value': 'Shop Weekdays 8-22'},
                            {'label': 'Shop Weekdays open all day', 'value': 'Shop Weekdays open all day'},
                            {'label': 'Shop open 7 days a week', 'value': 'Shop open 7 days a week'},
                            {'label': 'Seasonal Hotel small', 'value': 'Seasonal Hotel small'},
                            {'label': 'Seasonal Hotel medium', 'value': 'Seasonal Hotel medium'},
                            {'label': 'Seasonal Hotel large', 'value': 'Seasonal Hotel large'},
                            {'label': 'Hotel Always open small', 'value': 'Hotel Always open small'},
                            {'label': 'Hotel Always open medium', 'value': 'Hotel Always open medium'},
                            {'label': 'Hotel Always open large', 'value': 'Hotel Always open large'},
                         ],
                        placeholder="Select:",
                    ),
                ],width=3),
                dbc.Col([
                    html.Br(),
                    html.Br(),
                    daq.LEDDisplay(
                        id='LED-display-Comm',
                        label="Area [\u33A1]",
                        backgroundColor="#FF5E5E",
                        value=98,
                        size=100
                    ),
                    html.Br(),
                    dcc.Slider(
                        id='value_Area_Res',
                        dots=1,
                        min=10,
                        max=300,
                        step=10,
                        value=98,
                    ),
                ], width=9),
            ]),
            dbc.Row([
                dcc.Dropdown(
                    id='menu_res',
                    style={'display': 'none'}
                ),
                daq.BooleanSwitch(
                    id='aircond_boolean_switch',
                    style={'display': 'none'}
                ),
                daq.BooleanSwitch(
                    id='HP_boolean_switch',
                    style={'display': 'none'}
                ),
                daq.BooleanSwitch(
                    id='dw_boolean_switch',
                    style={'display': 'none'}
                ),
                dcc.Dropdown(
                    id='menu_ind',
                    disabled=True,
                    style={'display': 'none'}
                ),
            ]),
        ])
    elif tab == 'Industrial':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Label(['Type:'], style={'font-weight': 'bold'}),
                    html.Br(),
                    html.Br(),
                    dcc.Dropdown(
                        id='menu_ind',
                        options=[
                            {'label': 'Confectionery industry', 'value': 'Confectionery industry'},
                            {'label': 'Wine Producer', 'value': 'Wine Producer'},
                            {'label': 'Bubbly Wine Producer', 'value': 'Bubbly Wine Producer'},
                            {'label': 'Metal-working', 'value': 'Metal-working'}],
                       )
                    ], width=4),
                ]),
            html.Div([
                dcc.Slider(
                    id='value_Area_Res',
                ),
                dcc.Dropdown(
                    id='menu_res',
                ),
                daq.BooleanSwitch(
                    id='dw_boolean_switch',
                ),
                daq.BooleanSwitch(
                    id='aircond_boolean_switch',
                ),
                daq.BooleanSwitch(
                    id='HP_boolean_switch',
                ),
                dcc.Dropdown(
                    id='menu_comm',
                ),
            ], style={'display': 'none'}),
        ]),

# _______________________________________________________________________________
# callbacks to display values with LED
@app.callback(
    dash.dependencies.Output('LED-display-Res', 'value'),
    [dash.dependencies.Input('value_Area_Res', 'value')]
)
def update_outputRes(value):
    return str(value)

@app.callback(
    dash.dependencies.Output('LED-display-Comm', 'value'),
    [dash.dependencies.Input('value_Area_Res', 'value')]
)
def update_outputOff(value):
    return str(value)

# callback to update dropdown options in residential tab
@app.callback(
    dash.dependencies.Output('menu_res', 'options'),
    [dash.dependencies.Input('npeople_numeric_input', 'value')]
)
def update_options(value):
    if value==1:
        options=[
            {"label": "Single with work", 'value': 'Single with work'},
            {"label": "Single man, 30 - 64 years, without work", 'value': 'Single man, 30 - 64 years, without work'},
            {"label": "Single man, 30 - 64 age, with work", 'value': 'Single man, 30 - 64 age, with work'},
            {"label": "Single woman, 30 - 64 years, without work", 'value': 'Single woman, 30 - 64 years, without work'},
            {"label": "Single woman, 30 - 64 years, with work", 'value': 'Single woman, 30 - 64 years, with work'},
            {"label": "Single, Retired Man", 'value': 'Single, Retired Man'},
            {"label": "Student", 'value': 'Student'},
            ]
        return options
    elif value==2:
        options=[
            {"label": "Family, 1 child, 1 at work, 1 at home", 'value': 'Family, 1 child, 1 at work, 1 at home'},
            {"label": "Single, 1 child, with work", 'value': 'Single, 1 child, with work'},
            {"label": "Couple under 30 years without work", 'value': 'Couple under 30 years without work'},
            {"label": "Shiftworker Couple", 'value': 'Shiftworker Couple'},
            {"label": "Couple, 30 - 64 age, with work", 'value': 'Couple, 30 - 64 age, with work'},
            {"label": "Couple, 30 - 64 years, without work", 'value': 'Couple, 30 - 64 years, without work'},
            {"label": "Couple, 30 - 64 years, 1 at work, 1 at home", 'value': 'Couple, 30 - 64 years, 1 at work, 1 at home'},
            {"label": "Couple with work around 40", 'value': 'Couple with work around 40'},
            {"label": "Couple over 65 years", 'value': 'Couple over 65 years'},
            {"label": "Retired Couple, no work", 'value': 'Retired Couple, no work'},
            ]
        return options
    elif value==3:
        options=[
            {"label": "Family, 1 child, with work", 'value': 'Family, 1 child, with work'},
            {"label": "Single man with 2 children, with work", 'value': 'Single man with 2 children, with work'},
            {"label": "Single woman, 2 children, with work", 'value': 'Single woman, 2 children, with work'},
            {"label": "Student Flatsharing", 'value': 'Student Flatsharing'},
            ]
        return options
    else:
        options=[
            {"label": "Family, 2 children, both at work", 'value': 'Family, 2 children, both at work'},
            {"label": "Family with 2 Children, one at work", 'value': 'Family with 2 Children, one at work'},
            {"label": "Family, 3 children, both with work", 'value': 'Family, 3 children, both with work'},
            {"label": "Family, 3 children, parents without work", 'value': 'Family, 3 children, parents without work'},
            {"label": "Single woman with 3 children, without work", 'value': 'Single woman with 3 children, without work'},
            ]
        return options


# _______________________________________________________________________________
# callback to ADD row to LOADS Summary
@app.callback(
    Output('adding-rows-table', 'data'),
    Output('adding-rows-table', 'columns'),
    [Input('submit-button', 'n_clicks'),
     Input('tabs_styled_with_props', 'value'),
     Input('editing_columns_name', 'value')
     ],
    State('adding-rows-table', 'data'),
)
def add_row(n_clicks, value, editing_columns_name, rows):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit-button' in changed_id:
        rows.append({
            'Name': editing_columns_name,
            'Type': value,
               })
        columns=[
            {"name": "Name", 'id': 'Name'},
            {"name": "Type", 'id': 'Type'},
            {"name": "Address", 'id': 'Address'},
            {"name": "POD", 'id': 'POD'},
        ]
    return rows, columns

#Hide Export Button if DataTable is Empty
@app.callback(
    Output("adding-rows-table", "css"),
    Input("adding-rows-table", "derived_virtual_data"),
)
def style_export_button(data):
    if data == []:
        return [{"selector": ".export", "rule": "display:none"}]
    else:
        return [{"selector": ".export", "rule": "display:block", "rule": "background-color:coral; color:white"}]



@app.callback(
    Output("adding-rows-table_prod", "css"),
    Input("adding-rows-table_prod", "derived_virtual_data"),
)
def style_export_button(data):
    if data == []:
        return [{"selector": ".export", "rule": "display:none"}]
    else:
        return [{"selector": ".export", "rule": "display:block", "rule": "background-color:darkseagreen; color:white"}]

# _______________________________________________________________________________________________________________________
# callback to update LOADS DataTable
#Residential
def loadresidential(city, value_Area_Res, menu_res, dw_boolean_switch, aircond_boolean_switch, HP_boolean_switch, editing_columns_name):
    df_LOAD = pd.DataFrame()
    City = "{}".format(city)
    lat = Nominatim(user_agent="my_user_agent").geocode(City + ',' + "Italy").latitude
    lon = Nominatim(user_agent="my_user_agent").geocode(City + ',' + "Italy").longitude

    State = Nominatim(user_agent="geoapiExercises").reverse(str(lat) + ',' + str(lon)).raw['address'].get('state', '')
    Nord_Ovest = ["Liguria", "Lombardia", "Piemonte", "Valle d\'Aosta/Vallée d\'Aoste"]
    Nord_Est = ["Emilia-Romagna", "Friuli-Venezia Giulia", "Trentino-Alto Adige/Südtirol", "Veneto"]
    Centro = ["Lazio", "Marche", "Toscana" , "Umbria"]
    Sud = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Molise", "Puglia"]
    Sicilia = ["Sicilia"]
    Sardegna = ["Sardegna"]


    df_LOAD[editing_columns_name] = df_Res[menu_res]


    if (State in Nord_Ovest):
        df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (-0.0085 * df_LOAD[editing_columns_name])
    elif (State in Nord_Est):
        df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (-0.1158 * df_LOAD[editing_columns_name])
    elif (State in Sud):
        df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (-0.1348 * df_LOAD[editing_columns_name])
    elif (State in Sicilia):
        df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (0.0551 * df_LOAD[editing_columns_name])
    elif (State in Sardegna):
        df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (0.1612 * df_LOAD[editing_columns_name])


    if (value_Area_Res>90):
        df_LOAD[editing_columns_name] = ((value_Area_Res-98)*0.0025 *df_LOAD[editing_columns_name]) + df_LOAD[editing_columns_name]


    if (dw_boolean_switch == False):
        df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] - (0.0818 * df_LOAD[editing_columns_name])

    if (aircond_boolean_switch == False):
        df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] - (df_HeatCool['AirCond'])


    if (HP_boolean_switch == True):
        if (State in Nord_Ovest):
            df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (df_HeatCool['Nord_Ovest'])
        elif (State in Nord_Est):
            df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (df_HeatCool['Nord_Est'])
        elif (State in Centro):
            df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (df_HeatCool['Centro'])
        elif (State in Sud):
            df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (df_HeatCool['Sud'])
        elif (State in Sicilia):
            df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (df_HeatCool['Sicilia'])
        elif (State in Sardegna):
            df_LOAD[editing_columns_name] = df_LOAD[editing_columns_name] + (df_HeatCool['Sardegna'])
    return df_LOAD.round(decimals=3)

# Commercial
def load_commercial(menu_comm, value_Area_Res, editing_columns_name):
    df_LOAD = pd.DataFrame()
    df_LOAD[editing_columns_name] = df_Comm[menu_comm]
    if (menu_comm== 'Office'):
        df_LOAD[editing_columns_name] = value_Area_Res * df_LOAD[editing_columns_name]
    if (menu_comm== 'Shop Weekdays 8-18'):
        df_LOAD[editing_columns_name] = value_Area_Res * df_LOAD[editing_columns_name]
    if (menu_comm== 'Shop Weekdays 8-22'):
        df_LOAD[editing_columns_name] = value_Area_Res * df_LOAD[editing_columns_name]
    if (menu_comm == 'Shop Weekdays open all day'):
        df_LOAD[editing_columns_name] = value_Area_Res * df_LOAD[editing_columns_name]
    if (menu_comm == 'Shop open 7 days a week'):
        df_LOAD[editing_columns_name] = value_Area_Res * df_LOAD[editing_columns_name]
    return df_LOAD.round(decimals=3)


# Industrial
def load_industrial(menu_ind, editing_columns_name):
    df_LOAD = pd.DataFrame()
    df_LOAD[editing_columns_name] = df_Ind[menu_ind]
    return df_LOAD.round(decimals=3)


df_LOADS = pd.DataFrame()
@app.callback(
    Output('editing_columns_cons', 'data'),
    [Input('submit-button', 'n_clicks'),
     Input('tabs_styled_with_props', 'value'),
     Input('city', 'value'),
     Input('value_Area_Res', 'value'),
     Input('menu_res', 'value'),
     Input('dw_boolean_switch', 'on'),
     Input('aircond_boolean_switch', 'on'),
     Input('HP_boolean_switch', 'on'),
     Input('menu_comm', 'value'),
     Input('menu_ind', 'value'),
     ],
    State('editing_columns_name', 'value'),
   )
def update_data(n_clicks, tab, city, value_Area_Res, menu_res, dw_boolean_switch, aircond_boolean_switch, HP_boolean_switch, menu_comm, menu_ind, editing_columns_name):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit-button' in changed_id:
        if tab == 'Residential':
            df_LOAD = loadresidential(city, value_Area_Res, menu_res, dw_boolean_switch, aircond_boolean_switch, HP_boolean_switch, editing_columns_name)
        if tab == 'Commercial':
            df_LOAD = load_commercial(menu_comm, value_Area_Res, editing_columns_name)
        if tab == 'Industrial':
            df_LOAD = load_industrial(menu_ind, editing_columns_name)
    df_LOADS[editing_columns_name] = df_LOAD[editing_columns_name]
    return df_LOADS.to_dict('records')



# ________________________________________________________________________
@app.callback(
    Output('editing_columns_cons', 'columns'),
    [Input('submit-button', 'n_clicks'),
     Input('editing_columns_name', 'value'),
     ],
    State('editing_columns_cons', 'columns'),
)
def update_columns(n_clicks,  editing_columns_name, existing_columns):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit-button' in changed_id:
        existing_columns.append({
            'id': editing_columns_name, 'name': editing_columns_name + ' [kW]',
             'deletable': True
        }),
    return existing_columns


# _______________________________________________________________________________
# ======= Callbacks for modal Popup PV=======
@app.callback(
    Output("markdown_prod", "style"),
    [Input("learn-more-button_prod", "n_clicks"),
     Input("markdown_close_prod", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button_prod":
            return {"display": "block"}
    return {"display": "none"}


@app.callback(
    dash.dependencies.Output('my-PV-display', 'value'),
    [dash.dependencies.Input('PV_POWER_numeric_input', 'value')]
)
def update_output(value):
    return str(value)




# callback to ADD rows to PV plant summary
@app.callback(
    Output('adding-rows-table_prod', 'data'),
    Output('adding-rows-table_prod', 'columns'),
    [Input('submit-button_prod', 'n_clicks'),
     Input('PV_POWER_numeric_input', 'value'),
     Input('editing_columns_name_prod', 'value')
     ],
    State('adding-rows-table_prod', 'data'),
)
def add_row(n_clicks, PV_POWER_numeric_input, editing_columns_name_prod, rows):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit-button_prod' in changed_id:
        rows.append({
            'Name': editing_columns_name_prod,
            'PV Nominal Power [kW]': PV_POWER_numeric_input,
        })
        columns = [
            {"name": "Name", 'id': 'Name'},
            {"name": "PV Nominal Power [kW]", 'id': 'PV Nominal Power [kW]'},
            {"name": "Address", 'id': 'Address'},
            {"name": "POD", 'id': 'POD'},
        ]
    return rows, columns

# _______________________________________________________________________________________________________________________
# callback to update PV plant DataTable
df_prod = pd.DataFrame()
@app.callback(
    Output('editing-columns_prod', 'data'),
    [Input('submit-button_prod', 'n_clicks'),
     Input('city', 'value'),
     Input('PV_POWER_numeric_input', 'value'),
     Input('loss', 'value'),
     Input('pvtechchoice', 'value'),
     Input('mountingplace', 'value'),
     ],
    State('editing_columns_name_prod','value'),
   )
def update_data(n_clicks, city, PV_POWER_numeric_input, loss, pvtechchoice, mountingplace, editing_columns_name_prod):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit-button_prod' in changed_id:
        df_PVGIS = callPVGIS_API(city, PV_POWER_numeric_input, loss, pvtechchoice, mountingplace, editing_columns_name_prod)
        df_prod[editing_columns_name_prod] = df_PVGIS[editing_columns_name_prod].values
    return df_prod.to_dict('records')


@app.callback(
    Output('editing-columns_prod', 'columns'),
    [Input('submit-button_prod', 'n_clicks'),
     Input('editing_columns_name_prod', 'value'),
     ],
    State('editing-columns_prod', 'columns'),
   )
def update_col(n_clicks,editing_columns_name_prod, existing_columns):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit-button_prod' in changed_id:
        existing_columns.append(
            {'id': editing_columns_name_prod, 'name': editing_columns_name_prod + ' [kW]',
             'deletable': True}),
    return existing_columns


# _______________________________________________________________________________________________________________________
# ======= Callbacks for modal popup MEMBERS=======
@app.callback(
    Output("markdown_members", "style"),
    [Input("learn_more_button_members", "n_clicks"),
     Input("markdown_close_members", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn_more_button_members":
            return {"display": "block"}
    return {"display": "none"}

# _______________________________________________________________________________
# # callback to download data frames (loads and production)
@app.callback(
    Output("download_df_load", "data"),
    [Input("save-button_load", "n_clicks"),
     ],
    State("editing_columns_cons", "data"))
def download_as_xlsx(n_clicks, table_data):
    df = pd.DataFrame.from_dict(table_data)
    if not n_clicks:
      raise PreventUpdate
    return dcc.send_data_frame(df.to_excel, ("LOADS Data" + '.' + "xlsx"))


@app.callback(
    Output("download_df_prod", "data"),
    Input("save-button_prod", "n_clicks"),
    State("editing-columns_prod", "data"))
def download_as_xlsx(n_clicks, table_data):
    df = pd.DataFrame.from_dict(table_data)
    if not n_clicks:
      raise PreventUpdate
    return dcc.send_data_frame(df.to_excel, "PV Data.xlsx")

@app.callback(
    Output("download_df_EC", "data"),
    [Input("save-button_EC", "n_clicks"),
     ],
    State("editing_columns_members", "data"))
def download_as_xlsx(n_clicks, table_data):
    df = pd.DataFrame.from_dict(table_data)
    if not n_clicks:
      raise PreventUpdate
    return dcc.send_data_frame(df.to_excel, ("EC Data" + '.' + "xlsx"))



@app.callback(
    Output("download_df_conf_EC", "data"),
    [Input("save_conf-button_EC", "n_clicks"),
     ],
    State("datatable_ECsummary2", "data"))
def download_as_xlsx(n_clicks, table_data):
    df = pd.DataFrame.from_dict(table_data)
    if not n_clicks:
      raise PreventUpdate
    return dcc.send_data_frame(df.to_excel, ("EC Summary Configuration" + '.' + "xlsx"))



#callback for updating Lottie animation Consumer-Producer-Prosumer
@app.callback(
    Output('ImageConsProdPros', 'url'),
    [Input('member_type', 'value')])
def updategraphs(value):
    if value=="Consumer":
        return "assets/Consumer.json"
    elif value=="Producer":
        return "assets/Producer.json"
    elif value=="Prosumer":
        return "assets/Prosumer.json"

# callback for MEMBERS Popup content
@app.callback(
    Output('define_perc_prodcons', 'children'),
    [Input('member_type', 'value'),
     ])
def updategraphs(value):
    if value=="Consumer":
        return html.Div([
            html.Br(),
            dcc.Dropdown(
                id='dropdown_members_cons',
                placeholder="Select a Load",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label(['Average Energy Cost [EUR/MWh]:'],
                               style={'font-weight': 'bold', 'color': 'white'}),
                    html.Br(),
                    daq.NumericInput(
                        id='average_energy_cost',
                        labelPosition='bottom',
                        value=150,
                        min=40,
                        max=900,
                    ),
                ]),
                dbc.Col([
                    daq.BooleanSwitch(
                        id='selfcons_boolean_switch',
                        style={'display': 'none'}
                    ),
                ])
            ]),
            dcc.Input(
                id="input_circular_prod", style={'display': 'none'}),
            dcc.Dropdown(
                id='dropdown_members_prod',
                style={'display': 'none'}
            ),
            daq.BooleanSwitch(
                id='detr_boolean_switch',
                style={'display': 'none'}
            )
        ])
    elif value=="Producer":
        return html.Div([
            dbc.Row([
                dbc.Col([
                    daq.NumericInput(
                        id='average_energy_cost',
                        style={'display': 'none'}
                        ),
                    ]),
                dbc.Col([
                    daq.BooleanSwitch(
                        id='selfcons_boolean_switch',
                        style={'display': 'none'}
                    ),
                ])
            ]),
            html.Br(),
            dcc.Dropdown(
                id='dropdown_members_prod',
                placeholder="Select a PV Plant",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.H3(["Percentage of ownership of the plant"], style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'white'}),
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Slider(
                id="slider_circular_prod", min=1, max=100,
                marks={
                    1: '1%',
                    10: '10%',
                    20: '20%',
                    30: '30%',
                    40: '40%',
                    50: '50%',
                    60: '60%',
                    70: '70%',
                    80: '80%',
                    90: '90%',
                    100: '100%',
                },
                value=100
            ),
            html.Br(),
            dcc.Input(id="input_circular_prod", type="number", min=1, max=100, value=100, placeholder="% PV Plant"),
            html.Br(),
            html.Br(),
            daq.BooleanSwitch(
                id='detr_boolean_switch',
                on=True,
                vertical=True,
                label="Energy Saving Bonus (50% deduction)",
                labelPosition="top",
                color="yellow",
            ),
            html.Br(),
            dcc.Dropdown(
                id='dropdown_members_cons',
                style={'display': 'none'}
            ),
        ])
    elif value=="Prosumer":
        return html.Div([
            dcc.Dropdown(
                id='dropdown_members_prod',
                placeholder="Select a PV Plant",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.H3(["Percentage of ownership of the plant"],
                    style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'white'}),
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Slider(
                id="slider_circular_prod", min=1, max=100,
                marks={
                    1: '1%',
                    10: '10%',
                    20: '20%',
                    30: '30%',
                    40: '40%',
                    50: '50%',
                    60: '60%',
                    70: '70%',
                    80: '80%',
                    90: '90%',
                    100: '100%',
                },
                value=100
            ),
            html.Br(),
            dcc.Input(id="input_circular_prod", type="number", min=1, max=100, value=100, placeholder="% PV Plant"),
            html.Br(),
            html.Br(),
            daq.BooleanSwitch(
                id='detr_boolean_switch',
                on=True,
                vertical=True,
                label="Energy Saving Bonus (50% deduction)",
                labelPosition="top",
                color="yellow",
            ),
            html.Br(),
            html.Br(),
            dcc.Dropdown(
                id='dropdown_members_cons',
                placeholder="Select a Load",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label(['Average Energy Cost [EUR/MWh]:'],
                               style={'font-weight': 'bold', 'color': 'white'}),
                    html.Br(),
                    daq.NumericInput(
                        id='average_energy_cost',
                        labelPosition='bottom',
                        value=150,
                        min=40,
                        max=900,
                    ),
                ]),
                dbc.Col([
                    daq.BooleanSwitch(
                        id='selfcons_boolean_switch',
                        on=False,
                        vertical=True,
                        label="Real Self Consumption",
                        labelPosition="top",
                        color="yellow",
                    ),
                ])
            ]),

        ])


# circular callback for % Ownership of PV Plants
@app.callback(
    Output("input_circular_prod", "value"),
    Output("slider_circular_prod", "value"),
    Input("input_circular_prod", "value"),
    Input("slider_circular_prod", "value"),
)
def callback(input_value, slider_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = input_value if trigger_id == "input_circular_prod" else slider_value
    return value, value

# circular callback for GSE incentive distribution percentage % to PV Plants owners
@app.callback(
    Output("input_circular_incentive", "value"),
    Output("slider_circular_incentive", "value"),
    Input("input_circular_incentive", "value"),
    Input("slider_circular_incentive", "value"),
)
def callback(input_value, slider_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = input_value if trigger_id == "input_circular_incentive" else slider_value
    return value, value

# circular callback for GSE incentive distribution percentage % to PV Plants owners
@app.callback(
    Output("input_circular_incentive2", "value"),
    Output("slider_circular_incentive2", "value"),
    Input("input_circular_incentive2", "value"),
    Input("slider_circular_incentive2", "value"),
)
def callback(input_value, slider_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = input_value if trigger_id == "input_circular_incentive2" else slider_value
    return value, value



#  callback to disable Boolean Switch
@app.callback(
    Output("selfcons_boolean_switch", "on"),
    Output("selfcons_boolean_switch", "disabled"),
    Input("input_circular_prod", "value"),
)
def callback(input_value):
    if (input_value != 100):
        return False, True
    else:
        return True, False


df_members=pd.DataFrame()
# callbacks to make datatable MEMBERS
@app.callback(
    Output('editing_columns_members', 'data'),
    [Input('LOADScontainer_data', 'data'),
     Input('PVcontainer_data', 'data'),
     Input('add_members', 'n_clicks'),
     Input('member_type', 'value'),
     Input('dropdown_members_cons', 'value'),
     Input('dropdown_members_prod', 'value'),
     Input('input_circular_prod', 'value'),
     Input('selfcons_boolean_switch', 'on'),
     ],
    State('name', 'value'),
   )
def update_data(rows1, rows2, n_clicks, member_type, dropdown_members_cons, dropdown_members_prod, input_circular_prod, on, name):
    df_loadss = pd.DataFrame(rows1)
    df_PV = pd.DataFrame(rows2)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'add_members' in changed_id:
        if member_type == 'Consumer':
            df_members[name + " Consumption"] = df_loadss[dropdown_members_cons]
            df_members[name + " Production"] = [0] * 8760
            df_members[name + " Real Self Cons"] = [0] * 8760
            return df_members.to_dict('records')

        if member_type == 'Producer':
            df_members[name + " Consumption"] = [0] * 8760
            df_members[name + " Production"] = df_PV[dropdown_members_prod]*(input_circular_prod/100)
            df_members[name + " Real Self Cons"] = [0] * 8760
            return df_members.to_dict('records')

        if member_type == 'Prosumer':
            df_members[name + " Consumption"] = df_loadss[dropdown_members_cons]
            df_members[name + " Production"] = df_PV[dropdown_members_prod]*(input_circular_prod/100)
            if on==True:
                df_members[name + " Real Self Cons"] = df_members[[name + " Consumption", name + " Production"]].min(axis=1)
            else:
                df_members[name + " Real Self Cons"] = [0] * 8760
            return df_members.to_dict('records')


# ________________________________________________________________________
@app.callback(
    Output('editing_columns_members', 'columns'),
    [Input('add_members', 'n_clicks'),
     Input('name', 'value'),
     ],
    State('editing_columns_members', 'columns'),
)
def update_columns(n_clicks,  editing_columns_name, existing_columns):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'add_members' in changed_id:
        existing_columns.append({
            'id': editing_columns_name + " Consumption", 'name': editing_columns_name + " Consumption",
        }),
        existing_columns.append({
            'id': editing_columns_name + " Production", 'name': editing_columns_name + " Production",
        }),
        existing_columns.append({
            'id': editing_columns_name + " Real Self Cons", 'name': editing_columns_name + " Real Self Cons",
        }),
    return existing_columns


# # ________________________________________________________________________________________________________________________
# # Historical analysis graphs
#callback for updating plots in Consumption-graphs_Users
@app.callback(
    Output("graph_UsersCons", "figure"),
    Output("graph_BarMonths", "figure"),
    # Output("graph_BoxByDay", "figure"),
    # Output("graph_BoxByDayByHour", "figure"),
    # Output("graph_BoxByMonthByHour", "figure"),
    [Input("User_ID", "value"),
     Input('EC_Data', 'data'),
     ])
def create_graphsCons(User_ID, rows):
    df_members = pd.DataFrame(rows)
    df_cons = df_members.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    df_cons.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    # convert to montly data
    df_cons_montly = df_cons.resample('M', on='Date').sum()
    df_cons_montly.insert(loc=0,
                          column='Month',
                          value=range(1, 13))

    df_cons['Hour'] = df_cons['Date'].dt.hour
    df_cons['DayOfWeek'] = df_cons['Date'].dt.dayofweek
    df_cons['DayName'] = df_cons['Date'].dt.day_name()
    df_cons['Month'] = df_cons['Date'].dt.month
    df_cons['MonthName'] = df_cons['Date'].dt.month_name()
    df_cons['Year'] = df_cons['Date'].dt.year
    df_cons['Date_str'] = df_cons['Date'].dt.strftime('%Y-%m-%d')

    # F1 (ore di punta)	dalle 8:00 di mattina alle 19:00 dal lunedì al venerdì, festività nazionali escluse
    # F2 (ore intermedie)	dalle ore 7:00 alle ore 8:00 la mattina, dalle ore 19:00 alle ore 23:00 dal lunedì al venerdì e dalle ore 7:00 alle ore 23:00 il sabato, festività nazionali escluse
    # F3 (ore fuori punta)	dalle ore 00.00 alle ore 7.00 e dalle ore 23.00 alle ore 24.00 dal lunedì al sabato, la domenica e festivi tutte le ore della giornata

    # WD = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    # WDS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    # a = range(8, 19)
    # b = range(7, 24)
    # c = [7, 8, 19, 20, 21, 22]
    # d = [0, 1, 2, 3, 4, 5, 6, 23, 24]
    # Sat = ['Saturday']
    # Sun = ['Sunday']
    #
    # conditions = [
    #     (df_cons['DayName'].isin(WD)) & (df_cons['Hour'].isin(a)),
    #     (df_cons['DayName'].isin(WD) & df_cons['Hour'].isin(c)) | (
    #                 df_cons['DayName'].isin(Sat) & df_cons['Hour'].isin(b)),
    #     (df_cons['DayName'].isin(WDS) & df_cons['Hour'].isin(d)) | (df_cons['DayName'].isin(Sun))]
    # choices = ['F1', 'F2', 'F3']
    # df_cons['Zone'] = np.select(conditions, choices)

    graph_UsersCons = px.area(df_cons, x='Date', y=User_ID, template="simple_white") #color="Zone"
    graph_UsersCons.update_layout(
        title=dict(
            text='<b>Electrical load of Energy Community members [kW]</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis_title = 'Date',
        yaxis_title = 'Electrical load [kW]')

    graph_UsersCons.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    initial_range = [
        '2018-01-01', '2018-01-10'
    ]

    graph_UsersCons['layout']['xaxis'].update(range=initial_range)
    graph_UsersCons.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
            ])
        ),
        type='date'
    )
    # graph_BoxByDay = px.box(df_cons, x="DayName", y=User_ID, color="DayName", color_discrete_sequence=colDay, template="simple_white", category_orders={"DayName": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']})
    # graph_BoxByDay.update_layout(title_text='Box Plot Power [kW] by Day of Week', title_x=0.5)
    # graph_BoxByDay.update(layout_showlegend=False)

    # graph_BoxByDayByHour = px.box(df_cons, x='Hour', y=User_ID, color="DayOfWeek", facet_col="DayOfWeek",
    #                               boxmode="overlay", color_discrete_sequence=colDay, template="simple_white",
    #                               category_orders={"DayOfWeek": [0, 1, 2, 3, 4, 5, 6]}, facet_col_wrap=3,
    #                               facet_col_spacing=0.03, height=1000)
    # graph_BoxByDayByHour.update_layout(title_text='Box Plot Consumption [kW] by Day of Week & Hour', title_x=0.5)
    # graph_BoxByDayByHour.update(layout_showlegend=False)
    # graph_BoxByDayByHour.update_yaxes(matches=None)

    # graph_BoxByMonthByHour = px.box(df_cons, x="Hour", y=User_ID, color="MonthName", facet_col="MonthName",boxmode="overlay" ,color_discrete_sequence=cols, template="simple_white", facet_col_wrap=3, facet_col_spacing=0.03, height=1000,category_orders={"MonthName": ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']})
    # graph_BoxByMonthByHour.update_layout(title_text='Box Plot Power [kW] by Month & Hour', title_x=0.5)
    # graph_BoxByMonthByHour.update(layout_showlegend=False)
    # graph_BoxByMonthByHour.update_yaxes(matches=None)

    graph_BarMonths = px.bar(df_cons_montly, x='Month', y=User_ID, template="simple_white")
    graph_BarMonths.update_layout(
        title=dict(
            text='<b>Energy Consumption [kWh] by Month</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis_title = 'Month',
        yaxis_title = 'Electrical energy [kWh]')
    graph_BarMonths.update(layout_showlegend=False)
    graph_BarMonths.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1")

    return (graph_UsersCons,graph_BarMonths)

# ____________________________________________________________________________________________________________________________
#callback for updating Carpet Plot in Consumption tab
@app.callback(
    Output("graph_Carpet", "figure"),
    [Input("User", "value"),
     Input('EC_Data', 'data'),
     ])
def create_carpet(User, rows):
    df_members = pd.DataFrame(rows)
    df_cons = df_members.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    df_cons.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    df_cons['Hour'] = df_cons['Date'].dt.hour
    df_cons['DayOfWeek'] = df_cons['Date'].dt.dayofweek
    df_cons['DayName'] = df_cons['Date'].dt.day_name()
    df_cons['Month'] = df_cons['Date'].dt.month
    df_cons['MonthName'] = df_cons['Date'].dt.month_name()
    df_cons['Year'] = df_cons['Date'].dt.year
    df_cons['Date_str'] = df_cons['Date'].dt.strftime('%Y-%m-%d')

    graph_Carpet = go.Figure(data=go.Heatmap({'x': df_cons.Hour.tolist(), 'y': df_cons.Date_str.tolist(), 'z': df_cons['{}'.format(User)]}, colorscale=colCarp[::-1], connectgaps=True))
    graph_Carpet.update_layout(
        title=dict(
            text='<b>Yearly Energy Consumption [kWh]</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis_title = 'Hour',
        yaxis_title = 'Energy Consumption [kWh]')
    graph_Carpet.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1")

    return graph_Carpet

# ______________________________________________________________________________________________________________________
# callback for updating plots in Production-graphs_Users
@app.callback(
    Output("graph_UsersProd", "figure"),
    Output("graph_BarMonthsProd", "figure"),
    [Input("Prod_ID", "value"),
     Input('EC_Data', 'data'),
     ])
def create_graphsProd(Prod_ID, rows):
    df_members = pd.DataFrame(rows)
    df_prod = df_members.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    df_prod.insert(loc=0,
                 column='Date',
                 value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    # convert to montly data
    df_prod_montly = df_prod.resample('M', on='Date').sum()
    df_prod_montly.insert(loc=0,
                        column='Month',
                        value=range(1, 13))

    # get the hour,month and year from the datetime column
    df_prod['Hour'] = df_prod['Date'].dt.hour
    df_prod['DayOfWeek'] = df_prod['Date'].dt.dayofweek
    df_prod['DayName'] = df_prod['Date'].dt.day_name()
    df_prod['Month'] = df_prod['Date'].dt.month
    df_prod['MonthName'] = df_prod['Date'].dt.month_name()
    df_prod['Year'] = df_prod['Date'].dt.year
    df_prod['Date_str'] = df_prod['Date'].dt.strftime('%Y-%m-%d')

    graph_UsersProd = px.area(df_prod, x='Date', y=Prod_ID, template="simple_white")
    graph_UsersProd.update_layout(
        title=dict(
            text='<b>Electrical Production of Energy Community members [kW]</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis_title = 'Date',
        yaxis_title = 'Electrical Production [kW]')
    graph_UsersProd.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    initial_range = [
        '2018-01-01', '2018-01-10'
    ]

    graph_UsersProd['layout']['xaxis'].update(range=initial_range)
    graph_UsersProd.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
            ])
        )
    )

    graph_BarMonthsProd = px.bar(df_prod_montly, x="Month", y=Prod_ID,  template="simple_white")
    graph_BarMonthsProd.update_layout(
        title=dict(
            text='<b>Energy Production [kWh] by Month</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis_title = 'Month',
        yaxis_title = 'Energy Production [kWh]')
    graph_BarMonthsProd.update(layout_showlegend=False)
    graph_BarMonthsProd.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1")



    # graph_BoxByDayByHourProd = px.box(df_prod, x="Hour", y=Prod_ID, color="DayOfWeek", facet_col="DayOfWeek",
    #                                   boxmode="overlay", color_discrete_sequence=colDay, template="simple_white",
    #                                   category_orders={"DayOfWeek": [0, 1, 2, 3, 4, 5, 6]}, facet_col_wrap=3,
    #                                   facet_col_spacing=0.03, height=1000)
    # graph_BoxByDayByHourProd.update_layout(title_text='Box Plot Power Production [kW] by Day of Week & Hour',
    #                                        title_x=0.5)
    # graph_BoxByDayByHourProd.update(layout_showlegend=False)
    # graph_BoxByDayByHourProd.update_yaxes(matches=None)

    return (graph_UsersProd,graph_BarMonthsProd)

# # callback for updating Carpet Plot in Production tab
@app.callback(
    Output("graph_CarpetProd", "figure"),
    [Input("Prod", "value"),
     Input('EC_Data', 'data'),
     ])
def create_carpet(Prod, rows):
    df_members = pd.DataFrame(rows)
    df_prod = df_members.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    df_prod.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    # get the hour,month and year from the datetime column
    df_prod['Hour'] = df_prod['Date'].dt.hour
    df_prod['DayOfWeek'] = df_prod['Date'].dt.dayofweek
    df_prod['DayName'] = df_prod['Date'].dt.day_name()
    df_prod['Month'] = df_prod['Date'].dt.month
    df_prod['MonthName'] = df_prod['Date'].dt.month_name()
    df_prod['Year'] = df_prod['Date'].dt.year
    df_prod['Date_str'] = df_prod['Date'].dt.strftime('%Y-%m-%d')

    graph_CarpetProd = go.Figure(data=go.Heatmap({'x': df_prod.Hour.tolist(), 'y': df_prod.Date_str.tolist(), 'z': df_prod['{}'.format(Prod)]}, colorscale=colCarp[::-1], connectgaps=True))
    graph_CarpetProd.update_layout(
        title=dict(
            text='<b>Yearly Energy Production [kWh]</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis_title = 'Hour',
        yaxis_title = 'Energy Production [kWh]')

    return graph_CarpetProd

# ____________________________________________________________________________________________________________________________________________________________________
# #callback for updating line plot in Exploratory Data Analysis Community level
@app.callback(
    Output('graph_ProdCons', 'figure'),
    # Output('graph_SelfCons', 'figure'),
    [Input('menu', 'value'),
     Input('EC_Data', 'data'),
     ])
def update_graph(value, rows):
    df_members = pd.DataFrame(rows)
    df_cons = df_members.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    df_cons.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    df_cons['Hour'] = df_cons['Date'].dt.hour
    df_cons['DayOfWeek'] = df_cons['Date'].dt.dayofweek
    df_cons['DayName'] = df_cons['Date'].dt.day_name()
    df_cons['Month'] = df_cons['Date'].dt.month
    df_cons['MonthName'] = df_cons['Date'].dt.month_name()
    df_cons['Year'] = df_cons['Date'].dt.year
    df_cons['Date_str'] = df_cons['Date'].dt.strftime('%Y-%m-%d')

    df_cons['EC Consumption [kW]'] = df_cons.iloc[:, 1:(len(df_cons.columns) - 7)].sum(axis=1)


    df_prod = df_members.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    df_prod.insert(loc=0,
                 column='Date',
                 value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    # get the hour,month and year from the datetime column
    df_prod['Hour'] = df_prod['Date'].dt.hour
    df_prod['DayOfWeek'] = df_prod['Date'].dt.dayofweek
    df_prod['DayName'] = df_prod['Date'].dt.day_name()
    df_prod['Month'] = df_prod['Date'].dt.month
    df_prod['MonthName'] = df_prod['Date'].dt.month_name()
    df_prod['Year'] = df_prod['Date'].dt.year
    df_prod['Date_str'] = df_prod['Date'].dt.strftime('%Y-%m-%d')
    df_prod['EC Production [kW]'] = df_prod.iloc[:, 1:(len(df_prod.columns) - 7)].sum(axis=1)

    df_community = df_cons[["Date", "EC Consumption [kW]"]]
    df_community = pd.concat([df_community, df_prod['EC Production [kW]']], axis=1)
    # convert to montly data
    df_montlycomm = df_community.resample('M', on='Date').sum()
    df_montlycomm.insert(loc=0,
                         column='Month',
                         value=range(1, 13))


    df_community['Month'] = df_community['Date'].dt.month
    df_community_filt = df_community[df_community['Month'] == value]
    return create_graphh(df_community_filt)
def create_graphh(df_community_filt):
    graph_ProdCons=go.Figure(
        data=[
            go.Scatter(
                x=df_community_filt["Date"],
                y=df_community_filt["EC Consumption [kW]"],
                line={"color": "red"},
                mode="lines",
                name="Community Consumption [kW]"),
            go.Scatter(
                x=df_community_filt["Date"],
                y=df_community_filt["EC Production [kW]"],
                line={"color": "green"},
                mode="lines",
                name="Community Production [kW]",
            ),
        ],
        layout=dict(template='simple_white'))
    graph_ProdCons.update_layout(
        template="none",
        title=dict(
            text='<b>Production vs Consumption in the Energy Community [kW]</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis_title = 'Date')
    # graph_SelfCons=px.bar(df_community_filt, y='EUR', x='Date', template="simple_white")
    # graph_SelfCons.update_layout(title_text='Incentives from GSE to the Energy Community [EUR]', title_x=0.5)

    return graph_ProdCons

# ______________________________________________________________________________________________________________________
# callback to see montly energy at Community level
@app.callback(
    Output('graph_EnergyCommunity', 'figure'),
    Output('graph_DonutCommunity', 'figure'),
    [Input('EC_Data', 'data'),
     ])
def update_graph(rows):
    df_members = pd.DataFrame(rows)

    df_cons = df_members.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    list_cons = list(pd.unique(list(next(zip(*map(str.split, list(df_cons)))))))
    total_cons=list(round(((df_cons.sum())/1000), 3))

    df_cons.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    df_cons['Hour'] = df_cons['Date'].dt.hour
    df_cons['DayOfWeek'] = df_cons['Date'].dt.dayofweek
    df_cons['DayName'] = df_cons['Date'].dt.day_name()
    df_cons['Month'] = df_cons['Date'].dt.month
    df_cons['MonthName'] = df_cons['Date'].dt.month_name()
    df_cons['Year'] = df_cons['Date'].dt.year
    df_cons['Date_str'] = df_cons['Date'].dt.strftime('%Y-%m-%d')

    df_cons['EC Consumption [kW]'] = df_cons.iloc[:, 1:(len(df_cons.columns) - 7)].sum(axis=1)

    df_prod = df_members.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    list_prod = list(pd.unique(list(next(zip(*map(str.split, list(df_prod)))))))
    total_prod=list(round(((df_prod.sum())/1000), 3))
    df_prod.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    # get the hour,month and year from the datetime column
    df_prod['Hour'] = df_prod['Date'].dt.hour
    df_prod['DayOfWeek'] = df_prod['Date'].dt.dayofweek
    df_prod['DayName'] = df_prod['Date'].dt.day_name()
    df_prod['Month'] = df_prod['Date'].dt.month
    df_prod['MonthName'] = df_prod['Date'].dt.month_name()
    df_prod['Year'] = df_prod['Date'].dt.year
    df_prod['Date_str'] = df_prod['Date'].dt.strftime('%Y-%m-%d')
    df_prod['EC Production [kW]'] = df_prod.iloc[:, 1:(len(df_prod.columns) - 7)].sum(axis=1)

    df_community = df_cons[["Date", "EC Consumption [kW]"]]
    df_community = pd.concat([df_community, df_prod['EC Production [kW]']], axis=1)

    # convert to montly data
    df_montlycomm = df_community.resample('M', on='Date').sum()
    df_montlycomm.insert(loc=0,
                         column='Month',
                         value=range(1, 13))

    df_community['Month'] = df_community['Date'].dt.month

    graph_EnergyCommunity= go.Figure(
        data=[
            go.Bar(
                x=df_montlycomm["Month"],
                y=df_montlycomm["EC Consumption [kW]"],
                name="Community Consumption [kWh]",
                marker_color='orangered'
            ),
            go.Bar(
                x=df_montlycomm["Month"],
                y=df_montlycomm["EC Production [kW]"],
                name="Community Production [kWh]",
                marker_color='#4CAF50'
            ),
        ],
        layout=dict(template='none'))
    graph_EnergyCommunity.update_layout(
        title=dict(
            text='<b>Monthly Production & Consumption [kWh]</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis=dict(
            title='Month',
            titlefont_size=16,
            tickfont_size=14,
        ),
        yaxis=dict(
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
        ),
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )
    graph_EnergyCommunity.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1")

    # Create subplots: use 'domain' type for Pie subplot

    graph_DonutCommunity = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                                         subplot_titles=['Consumption [MWh]', 'Production [MWh]'])
    graph_DonutCommunity.add_trace(go.Pie(labels=list_cons, values=total_cons, name='Yearly Consumption [MWh]', scalegroup='one'), 1, 1)
    graph_DonutCommunity.add_trace(go.Pie(labels=list_prod, values=total_prod, name='Yearly Production [MWh]', scalegroup='one'), 1, 2)
    # Use `hole` to create a donut-like pie chart
    graph_DonutCommunity.update_traces(
        hole=.4,
        hoverinfo='label+value+percent',
        textinfo='label+value',
        insidetextorientation='radial',
        textposition='inside',
        marker=dict(line=dict(color='#000000', width=1)))
    graph_DonutCommunity.update_layout(
        uniformtext_minsize=12, uniformtext_mode='hide',
        template='none',
        title=dict(
            text='<b>Yearly Consumption and Production in REC</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')))
    return graph_EnergyCommunity, graph_DonutCommunity




# callback to see montly energy at Community level
@app.callback(
    Output('graph_DonutCommunity2', 'figure'),
    [Input('EC_Data', 'data'),
     ])
def update_graph2(rows):
    df_members = pd.DataFrame(rows)

    df_cons = df_members.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    list_cons = list(pd.unique(list(next(zip(*map(str.split, list(df_cons)))))))
    total_cons=list(round(((df_cons.sum())/1000), 3))

    df_cons.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    df_cons['Hour'] = df_cons['Date'].dt.hour
    df_cons['DayOfWeek'] = df_cons['Date'].dt.dayofweek
    df_cons['DayName'] = df_cons['Date'].dt.day_name()
    df_cons['Month'] = df_cons['Date'].dt.month
    df_cons['MonthName'] = df_cons['Date'].dt.month_name()
    df_cons['Year'] = df_cons['Date'].dt.year
    df_cons['Date_str'] = df_cons['Date'].dt.strftime('%Y-%m-%d')

    df_cons['EC Consumption [kW]'] = df_cons.iloc[:, 1:(len(df_cons.columns) - 7)].sum(axis=1)

    df_prod = df_members.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    list_prod = list(pd.unique(list(next(zip(*map(str.split, list(df_prod)))))))
    total_prod=list(round(((df_prod.sum())/1000), 3))
    df_prod.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    # get the hour,month and year from the datetime column
    df_prod['Hour'] = df_prod['Date'].dt.hour
    df_prod['DayOfWeek'] = df_prod['Date'].dt.dayofweek
    df_prod['DayName'] = df_prod['Date'].dt.day_name()
    df_prod['Month'] = df_prod['Date'].dt.month
    df_prod['MonthName'] = df_prod['Date'].dt.month_name()
    df_prod['Year'] = df_prod['Date'].dt.year
    df_prod['Date_str'] = df_prod['Date'].dt.strftime('%Y-%m-%d')
    df_prod['EC Production [kW]'] = df_prod.iloc[:, 1:(len(df_prod.columns) - 7)].sum(axis=1)


    # Create subplots: use 'domain' type for Pie subplot

    graph_DonutCommunity2 = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                                         subplot_titles=['Consumption [MWh]', 'Production [MWh]'])
    graph_DonutCommunity2.add_trace(go.Pie(labels=list_cons, values=total_cons, name='Yearly Consumption [MWh]', scalegroup='one'), 1, 1)
    graph_DonutCommunity2.add_trace(go.Pie(labels=list_prod, values=total_prod, name='Yearly Production [MWh]', scalegroup='one'), 1, 2)

    # Use `hole` to create a donut-like pie chart
    graph_DonutCommunity2.update_traces(
        hole=.4,
        hoverinfo='label+value+percent',
        textinfo='label+value',
        insidetextorientation='radial',
        textposition='inside',
        marker=dict(line=dict(color='#000000', width=1)))
    graph_DonutCommunity2.update_layout(
        uniformtext_minsize=12, uniformtext_mode='hide',
        template='none',
        title=dict(
            text='<b>Yearly Consumption and Production in REC</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')))

    return graph_DonutCommunity2




# callback to see EC benefits
@app.callback(
    Output('EC_Consumption_LED','value'),
    Output('EC_Production_LED','value'),
    Output('RealSelf_LED', 'value'),
    Output('Shared_electricity_LED', 'value'),
    Output('ingrid_LED', 'value'),
    Output('fromgrid_LED', 'value'),
    Output('GSE_Incentive_LED','value'),
    Output('SaleEnergy_LED','value'),
    Output('Savings_LED', 'value'),
    Output('CO2Red_LED','value'),
    [Input('EC_Data', 'data'),
     ])
def update_values(rows):
    df_members = pd.DataFrame(rows)
    users = pd.unique(list(next(zip(*map(str.split, list(df_members))))))
    for user in users:
        df_members.insert(loc=0,
                          column=user + ' Energy withdrawn from the grid',
                          value=df_members[user + ' Consumption'] - df_members[user + ' Real Self Cons'])
        df_members.insert(loc=0,
                          column=user + ' Energy fed into the grid',
                          value=df_members[user + ' Production'] - df_members[user + ' Real Self Cons'])


    df_cons = df_members.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    df_cons.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    df_cons['Hour'] = df_cons['Date'].dt.hour
    df_cons['DayOfWeek'] = df_cons['Date'].dt.dayofweek
    df_cons['DayName'] = df_cons['Date'].dt.day_name()
    df_cons['Month'] = df_cons['Date'].dt.month
    df_cons['MonthName'] = df_cons['Date'].dt.month_name()
    df_cons['Year'] = df_cons['Date'].dt.year
    df_cons['Date_str'] = df_cons['Date'].dt.strftime('%Y-%m-%d')

    # calcolo il totale dei vari utenti (sommo le colonne) ottengo colonna TOT 8760 valori
    df_cons['EC Consumption [kW]'] = df_cons.iloc[:, 1:(len(df_cons.columns) - 7)].sum(axis=1)
    # calcolo il valore totale annuale
    EC_Cons = round((df_cons['EC Consumption [kW]'].sum()/1000), 2),


    df_prod = df_members.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    df_prod.insert(loc=0,
                   column='Date',
                   value=pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left'))

    # get the hour,month and year from the datetime column
    df_prod['Hour'] = df_prod['Date'].dt.hour
    df_prod['DayOfWeek'] = df_prod['Date'].dt.dayofweek
    df_prod['DayName'] = df_prod['Date'].dt.day_name()
    df_prod['Month'] = df_prod['Date'].dt.month
    df_prod['MonthName'] = df_prod['Date'].dt.month_name()
    df_prod['Year'] = df_prod['Date'].dt.year
    df_prod['Date_str'] = df_prod['Date'].dt.strftime('%Y-%m-%d')
    # calcolo il totale dei vari utenti (sommo le colonne) ottengo colonna TOT 8760 valori
    df_prod['EC Production [kW]'] = df_prod.iloc[:, 1:(len(df_prod.columns) - 7)].sum(axis=1)
    # calcolo il valore totale annuale
    EC_Prod = round((df_prod['EC Production [kW]'].sum() / 1000), 2),


    df_community = df_cons[["Date", "EC Consumption [kW]"]]
    df_community = pd.concat([df_community, df_prod['EC Production [kW]']], axis=1)

    df_withdrawn_from = df_members.filter(regex='withdrawn from')
    # get the total column in df_members Energy withdrawn from the grid
    df_members['Energy withdrawn from the grid'] = df_withdrawn_from.iloc[:, 0:(len(df_withdrawn_from.columns))].sum(axis=1)
    # get the total value Energy withdrawn from the grid [MWh]
    Energy_fromthegrid = round((df_members['Energy withdrawn from the grid'].sum() / 1000), 3)


    df_fed_into = df_members.filter(regex='fed into')
    # get the total column in df_members Energy fed into the grid
    df_members['Energy fed into the grid'] = df_fed_into.iloc[:, 0:(len(df_fed_into.columns))].sum(axis=1)
    # get the annual total value Energy withdrawn from the grid
    # ELECTRICITY PRICE  50.1 [euro / MWh]
    Energy_intothegrid = round((df_members['Energy fed into the grid'].sum() / 1000), 2)
    SaleEnergy=round((Energy_intothegrid* 50.1),2)


    df_community['Shared electricity [kW]'] = df_members[['Energy fed into the grid', 'Energy withdrawn from the grid']].min(axis=1)
    Shared_electricity=round((df_community['Shared electricity [kW]'].sum() / 1000), 2)

    # # 118.2 EUR/MWh is the incentive from GSE to EC
    # Per la creazione della comunità 110 [euro/MWh]
    # Tariffa di distribuzione  7.61	[euro/MWh]
    # Tariffa di trasmissione 0.61	[euro/MWh]
    df_community['GSEInc'] = df_community['Shared electricity [kW]'] * 0.11822
    GSEInc = round(df_community['GSEInc'].sum(), 2),


    df_realselfcons = df_members.filter(regex='Real Self Cons')
    df_realselfcons = df_realselfcons.loc[:, (df_realselfcons != 0).any(axis=0)]
    df_members['Real Self Cons[kW]'] = df_realselfcons.iloc[:, 0:(len(df_realselfcons.columns))].sum(axis=1)
    Energy_SelfCons = round((df_members['Real Self Cons[kW]'].sum() / 1000), 2)
    Savings=round((Energy_SelfCons* 150),2)

    # ISPRA- Istituto Superiore per la Protezione e la Ricerca Ambientale 2020 (276.4 g/kWh el)
    CO2Red = round((df_prod['EC Production [kW]'].sum()) * 276.4 * 10e-6, 2)
    return EC_Cons, EC_Prod, Energy_SelfCons, Shared_electricity, Energy_intothegrid, Energy_fromthegrid, GSEInc, SaleEnergy, Savings, CO2Red


# --------------------------------------------------------------------------------
# callback for Exploratory Data-Tab
@app.callback(
     dash.dependencies.Output('tabs-content-historical_data', 'children'),
    [dash.dependencies.Input('tabs-historical_data', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(id='graph_DonutCommunity'), width=12),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Button('Community', id='collapse-button3', n_clicks=0,
                                style={'background-color': 'steelblue', 'color': 'white', 'width': '100%',
                                       'height': '100%', 'textAlign': 'center'}),
                ]),

            ], justify='center'),
            html.Br(),
            dbc.Collapse([
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%",
                                       url="assets/59927-buzzing-round-button.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='EC_Consumption_LED',
                                    label="Yearly EC Consumption [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/PV.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='EC_Production_LED',
                                    label="Yearly EC Production [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Realself.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='RealSelf_LED',
                                    label="Yearly Real Self Consumption [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Virtualself.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='Shared_electricity_LED',
                                    label="Yearly Shared energy [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Grid.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='ingrid_LED',
                                    label="Energy fed into the grid [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/fromgrid.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='fromgrid_LED',
                                    label="Energy withdrawn from the grid [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                ]),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Euro.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='GSE_Incentive_LED',
                                    label="Yearly GSE Incentive [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/EUR.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='SaleEnergy_LED',
                                    label="Yearly Revenue from energy sold to the grid [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Savings.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='Savings_LED',
                                    label="Savings for non-purchased energy [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/CO2.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='CO2Red_LED',
                                    label="Annual Carbon dioxide avoided [t CO2/year]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                ]),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='graph_EnergyCommunity'), width=12),
                ]),
                html.Br(),
                html.Br(),
                html.Label(['Select a month:'], style={'font-weight': 'bold', 'color': 'navy'}),
                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                            id='menu',
                            options=[{'label': i, 'value': i} for i in range(1, 13)],
                            value=6,
                            placeholder="Month"
                        ), width=12),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='graph_ProdCons'), width=12),
                ]),
            ],
                id="collapse_COMM",
                is_open=False),
        ])
    if tab == 'tab-2':
        return html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col(),
                dbc.Col(),
                dbc.Col([
                    html.Button('LOADS', id='collapse-button1', n_clicks=0,
                                style={'background-color': 'orangered', 'color': 'white', 'width': '100%',
                                       'height': '100%', 'textAlign': 'center'}),
                ]),
                dbc.Col([
                    html.Button('PV Plants', id='collapse-button2', n_clicks=0,
                                style={'background-color': '#4CAF50', 'color': 'white', 'width': '100%',
                                       'height': '100%', 'textAlign': 'center'}),
                ]),
                dbc.Col(),
                dbc.Col(),
            ],justify='center'),
            dbc.Collapse([
                html.Label(['Select a community Member:'], style={'font-weight': 'bold', 'color': 'navy'}),
                dcc.Dropdown(id='User',
                             multi=False,
                             placeholder="Select a member"),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%",
                                       url="assets/59927-buzzing-round-button.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='EC_Consumption_member_LED',
                                    label="Yearly Consumption [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Realself.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='RealSelf_member_LED',
                                    label="Yearly Real Self Consumption [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/fromgrid.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='fromgrid_member_LED',
                                    label="Energy withdrawn from the grid [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Pay.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='Energy_expenditure_member_LED',
                                    label="Annual Energy expenditure [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                ], justify="center"),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col([dcc.Graph(id='graph_Carpet')], width=8),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Savings.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='Savings_member_LED',
                                    label="Savings for non-purchased energy [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Euro.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='GSE_Incentive_member1_LED',
                                    label="Yearly GSE Incentive [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                ]),
            ],
                id="collapse_LOADS",
                is_open=False),
            dbc.Collapse([
                html.Label(['Select a community Member:'], style={'font-weight': 'bold', 'color': 'navy'}),
                dcc.Dropdown(id='Prod',
                             multi=False,
                             placeholder="Select a member "),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%",
                                       url="assets/PV.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='EC_Production_member_LED',
                                    label="Yearly EC Production [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Grid.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='ingrid_member_LED',
                                    label="Energy fed into the grid [MWh/y]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/EUR.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='SaleEnergy_member_LED',
                                    label="Yearly Revenue from energy sold to the grid [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                Lottie(options=options, width="100%", height="100%", url="assets/Euro.json")),
                            dbc.CardBody([
                                daq.LEDDisplay(
                                    id='GSE_Incentive_member2_LED',
                                    label="Yearly GSE Incentive [EUR]",
                                    backgroundColor="cadetblue",
                                ),
                            ], style={'textAlign': 'center', 'color': 'navy', 'font-family': 'verdana'})
                        ], color="light"),
                    ], width=2, lg=2),
                ], justify='center'),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col([dcc.Graph(id='graph_CarpetProd')], width=8),
                ]),
            ],
                id="collapse_PV",
                is_open=False),
            html.Br(),
            html.Br(),
            dbc.Row([
                html.H3(["GSE incentive distribution percentage % to PV Plants owners"],
                        style={'font-style': 'italic', 'font-weight': 'bold', 'color': 'navy'}),
                html.Br(),
                html.Br(),
                html.Br(),
            ], justify='center'),
            dcc.Slider(
                id="slider_circular_incentive2", min=1, max=100,
                marks={
                    1: '1%',
                    10: '10%',
                    20: '20%',
                    30: '30%',
                    40: '40%',
                    50: '50%',
                    60: '60%',
                    70: '70%',
                    80: '80%',
                    90: '90%',
                    100: '100%',
                },
                value=80
            ),
            html.Br(),
            html.Br(),
            dbc.Row([
                dcc.Input(id="input_circular_incentive2", type="number", min=1, max=100, value=80,
                          placeholder="% GSE incentive"),
            ], justify='center'),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col(),
                dbc.Col(),
                dbc.Col([
                    html.Button('LOADS Graphs', id='collapse_buttonLOADS_Graphs', n_clicks=0,
                                style={'background-color': 'orangered', 'color': 'white', 'width': '100%',
                                       'height': '100%', 'textAlign': 'center'}),
                ]),
                dbc.Col([
                    html.Button('PV Plants Graphs', id='collapse_buttonPV_Graphs', n_clicks=0,
                                style={'background-color': '#4CAF50', 'color': 'white', 'width': '100%',
                                       'height': '100%', 'textAlign': 'center'}),
                ]),
                dbc.Col(),
                dbc.Col(),
            ], justify='center'),
            dbc.Collapse([
                html.Br(),
                dcc.Dropdown(id='User_ID',
                             multi=True,
                             placeholder="Select a community member User"),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='graph_UsersCons'), width=6),
                    dbc.Col(dcc.Graph(id='graph_BarMonths'), width=6),
                ]),
                html.Br(),
                html.Br(),
                html.Hr(),
                html.Hr(),
                html.Br(),
                dbc.Row([
                    html.Img(src=app.get_asset_url("12RESPONSIBLECONSUMPTIONANDPRODUCTION.png"))
                ], justify='center'),
            ],
                id="collapse_LOADSGraphs",
                is_open=False),
            dbc.Collapse([
                html.Br(),
                dcc.Dropdown(id='Prod_ID',
                             multi=True,
                             placeholder="Select a community member"),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='graph_UsersProd'), width=6),
                    dbc.Col(dcc.Graph(id='graph_BarMonthsProd'), width=6),
                ]),
                dbc.Row([
                    html.Img(src=app.get_asset_url("7AFFORDABLEANDCLEANENERGY.png"))
                ], justify='center'),
            ],
                id="collapse_PVGraphs",
                is_open=False),
        ])


@app.callback(
    Output("collapse_LOADSsetup", "is_open"),
    [Input("collapse-buttonLOADSsetup", "n_clicks")],
    [State("collapse_LOADSsetup", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_PVsetup", "is_open"),
    [Input("collapse-buttonPVsetup", "n_clicks")],
    [State("collapse_PVsetup", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_MEMBERSdefinition", "is_open"),
    [Input("collapse-buttonMEMBERSsetup", "n_clicks")],
    [State("collapse_MEMBERSdefinition", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open






@app.callback(
    Output("collapse_LOADS", "is_open"),
    [Input("collapse-button1", "n_clicks")],
    [State("collapse_LOADS", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse_PV", "is_open"),
    [Input("collapse-button2", "n_clicks")],
    [State("collapse_PV", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(
    Output("collapse_LOADSGraphs", "is_open"),
    [Input("collapse_buttonLOADS_Graphs", "n_clicks")],
    [State("collapse_LOADSGraphs", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_PVGraphs", "is_open"),
    [Input("collapse_buttonPV_Graphs", "n_clicks")],
    [State("collapse_PVGraphs", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_COMM", "is_open"),
    [Input("collapse-button3", "n_clicks")],
    [State("collapse_COMM", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open




@app.callback(
     dash.dependencies.Output('loading-output-4', 'children'),
    [dash.dependencies.Input('tabs-historical_data', 'value')])
def render_content2(tab):
    if tab == 'tab-1':
        time.sleep(2)
        message= html.Div([
            ])
        return message
    if tab == 'tab-2':
        time.sleep(3)
        message= html.Div([
            ])
        return message


# _______________________________________________________________________________
# callback to ADD row to EC Summary
@app.callback(
    Output('datatable_ECsummary2', 'data'),
    Output('datatable_ECsummary2', 'columns'),
    [Input('add_members', 'n_clicks'),
     Input('PVcontainer_data', 'data'),
     Input('member_type', 'value'),
     Input('name', 'value'),
     Input('dropdown_members_cons', 'value'),
     Input('dropdown_members_prod', 'value'),
     Input('input_circular_prod', 'value'),
     Input('detr_boolean_switch', 'on'),
     Input('selfcons_boolean_switch', 'on'),
     Input('average_energy_cost', 'value'),
     ],
    State('datatable_ECsummary2', 'data'),
    )
def ECsummary(n_clicks, data, value, name, load, prod, perc, detr, selfcons, CostoEnergia, rows):
    df = pd.DataFrame(data)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'add_members' in changed_id:
        if value == "Consumer":
            a = {
                'User_ID': name,
                'Load': load,
                'PVPlant': "",
                '% PV': "",
                'User_Type': value,
                'Bonus 50%': "",
                'Real Self Consumption': "",
                'Investment [EUR]': "0",
                'Average energy cost [EUR/MWh]': CostoEnergia,
                }
        elif value == "Producer":
            Potenza_installata = round((df[prod].max() * 1.24), 0)
            # Costospecifico_(impianto + installazione) [€/kWp]
            if Potenza_installata < 10:
                # EPC = 1186.06 * (1 + 0.08)
                # TPC = EPC * (1 + 0.2)
                # Costospecifico = TPC * (1 + 0.2)
                Costospecifico = 1186.06
            elif 10 <= Potenza_installata <= 1000:
                # EPC = 934.16 * (1 + 0.08)
                # TPC = EPC * (1 + 0.2)
                # Costospecifico = TPC * (1 + 0.2)
                Costospecifico = 934.16
            elif Potenza_installata > 1000:
                # EPC = 683.77 * (1 + 0.08)
                # TPC = EPC * (1 + 0.2)
                # Costospecifico = TPC * (1 + 0.2)
                Costospecifico = 683.77
            a = {
                'User_ID': name,
                'Load': "",
                'PVPlant': prod,
                '% PV': perc,
                'User_Type': value,
                'Bonus 50%': detr,
                'Real Self Consumption': "",
                'Investment [EUR]': Potenza_installata * Costospecifico * perc/100,
                'Average energy cost [EUR/MWh]': CostoEnergia,
                }
        elif value == "Prosumer":
            Potenza_installata = round((df[prod].max() * 1.24), 0)
            # Costospecifico_(impianto + installazione) [€/kWp]
            if Potenza_installata < 10:
                # EPC = 1186.06 * (1 + 0.08)
                # TPC = EPC * (1 + 0.2)
                # Costospecifico = TPC * (1 + 0.2)
                Costospecifico = 1186.06
            elif 10 <= Potenza_installata <= 1000:
                # EPC = 934.16 * (1 + 0.08)
                # TPC = EPC * (1 + 0.2)
                # Costospecifico = TPC * (1 + 0.2)
                Costospecifico = 934.16
            elif Potenza_installata > 1000:
                # EPC = 683.77 * (1 + 0.08)
                # TPC = EPC * (1 + 0.2)
                # Costospecifico = TPC * (1 + 0.2)
                Costospecifico = 683.77
            a = {
                'User_ID': name,
                'Load': load,
                'PVPlant': prod,
                '% PV': perc,
                'User_Type': value,
                'Bonus 50%': detr,
                'Real Self Consumption': selfcons,
                'Investment [EUR]': Potenza_installata * Costospecifico * perc/100,
                'Average energy cost [EUR/MWh]': CostoEnergia,

                }
        rows.append(a)
        columns = [
            {"name": "User_ID", 'id': 'User_ID'},
            {"name": "Load", 'id': 'Load'},
            {"name": "PVPlant", 'id': 'PVPlant'},
            {"name": "% PV", 'id': '% PV'},
            {"name": "User_Type", 'id': 'User_Type'},
            {"name": "Bonus 50%", 'id': 'Bonus 50%'},
            {"name": "Real Self Consumption", 'id': 'Real Self Consumption'},
            {"name": "Investment [EUR]", 'id': 'Investment [EUR]'},
            {"name": "Average energy cost [EUR/MWh]", 'id': 'Average energy cost [EUR/MWh]'},
            ]
    return rows, columns


# callback to update graph Economics tab according to Userselection (content)
@app.callback(Output('economics_graph', 'figure'),
              [Input('dropdown_member', 'value'),
               Input('EC_Data', 'data'),
               Input('datatable_conf_ECsummary', 'data'),
               Input('input_circular_incentive', 'value'),
               Input("xanchor", "value"),
               Input("yanchor", "value")
               ]
              )
def create_graph(Member, rows_data, rows_summary, value, pos_x, pos_y):
    n_years = 20
    df_comm = pd.DataFrame(rows_data)

    df_cons = df_comm.filter(regex='Consumption')
    df_cons = df_cons.loc[:, (df_cons != 0).any(axis=0)]
    cons = pd.unique(list(next(zip(*map(str.split, list(df_cons))))))
    # calcolo il totale dei vari utenti (sommo le colonne) ottengo colonna TOT 8760 valori
    df_cons['EC Consumption [kW]'] = df_cons.iloc[:, 0:(len(df_cons.columns))].sum(axis=1)

    users = pd.unique(list(next(zip(*map(str.split, list(df_comm))))))
    for user in users:
        df_comm.insert(loc=0,
                       column=user + ' Energy withdrawn from the grid',
                       value=df_comm[user + ' Consumption'] - df_comm[user + ' Real Self Cons'])
        df_comm.insert(loc=0,
                       column=user + ' Energy fed into the grid',
                       value=df_comm[user + ' Production'] - df_comm[user + ' Real Self Cons'])

    df_withdrawn_from = df_comm.filter(regex='withdrawn from')
    # get the total column in df_members Energy withdrawn from the grid
    df_comm['Energy withdrawn from the grid'] = df_withdrawn_from.iloc[:, 0:(len(df_withdrawn_from.columns))].sum(
        axis=1)

    df_fed_into = df_comm.filter(regex='fed into')
    # get the total column in df_members Energy fed into the grid
    df_comm['Energy fed into the grid'] = df_fed_into.iloc[:, 0:(len(df_fed_into.columns))].sum(axis=1)

    df_comm['Shared electricity [kW]'] = df_comm[['Energy fed into the grid', 'Energy withdrawn from the grid']].min(
        axis=1)
    df_comm['GSEIncEUR'] = df_comm['Shared electricity [kW]'] * 0.11822

    df_cons['GSEIncEUR Cons'] = df_comm['GSEIncEUR'] * (100-value)/100
    for user in cons:
        df_cons.insert(loc=0,
                       column=user + ' GSE Incentive',
                       value=(df_cons[user + ' Consumption'] * df_cons['GSEIncEUR Cons']) / df_cons[
                           'EC Consumption [kW]'])

    if Member in cons:
        GSE_Incentive_memberCONS = round((df_cons[Member + ' GSE Incentive'].sum()), 2)
    else:
        GSE_Incentive_memberCONS = 0

    # _________________________________________________________________________________________________________________
    df_prod = df_comm.filter(regex='Production')
    df_prod = df_prod.loc[:, (df_prod != 0).any(axis=0)]
    prod = pd.unique(list(next(zip(*map(str.split, list(df_prod))))))
    # calcolo il totale dei vari utenti (sommo le colonne) ottengo colonna TOT 8760 valori
    df_prod['EC Production [kW]'] = df_prod.iloc[:, 0:(len(df_prod.columns))].sum(axis=1)

    df_prod['GSEIncEUR Prod'] = df_comm['GSEIncEUR'] * (value/100)
    for user in prod:
        df_prod.insert(loc=0,
                       column=user + ' GSE Incentive',
                       value=(df_prod[user + ' Production'] * df_prod['GSEIncEUR Prod']) / df_prod[
                           'EC Production [kW]'])

    if Member in prod:
        GSE_Incentive_memberPROD = round((df_prod[Member + ' GSE Incentive'].sum()), 2)
    else:
        GSE_Incentive_memberPROD = 0

    GSE_Incentive_member = GSE_Incentive_memberCONS + GSE_Incentive_memberPROD



    df_ECdata = pd.DataFrame(rows_data)
    df_member = df_ECdata.filter(regex=Member)
    df_summary=pd.DataFrame(rows_summary)
    info_member = df_summary[df_summary['User_ID'] == Member]


    # Potenza_installata impianto reale[kWp]
    Potenza_installata = round((df_member[Member + " Production"].max() * 1.24), 0)

    # # Percentuale_proprietà 0-1 []
    # x = info_member.iloc[0]['% PV']
    # if pd.isna(x) == True:
    #     Percentuale_proprietà = 0
    # else:
    #     Percentuale_proprietà = (info_member.iloc[0]['% PV']) / 100

    # _______________________________________________________________________________________________________________
    # aggiungi colonna prelievi da rete Energy_fromthegrid
    df_member.insert(loc=3,
                     column=' Energy withdrawn from the grid',
                     value=df_member[Member + ' Consumption'] - df_member[Member + ' Real Self Cons']),
    Cons = round((df_member[Member + ' Consumption'].sum() / 1000), 2)

    # Autoconsumo reale [MWh]
    Energy_SelfCons = round((df_member[Member + ' Real Self Cons'].sum() / 1000), 2)
    Energy_fromthegrid = round((df_member[' Energy withdrawn from the grid'].sum() / 1000), 2)

    # _______________________________________________________________________________________________________________

    # aggiungi colonna immissioni in rete Energy_intothegrid
    df_member.insert(loc=4,
                     column=' Energy fed into the grid',
                     value=df_member[Member + ' Production'] - df_member[Member + ' Real Self Cons'])

    Prod = round((df_member[Member + ' Production'].sum() / 1000), 2)
    Energy_intothegrid = round((df_member[' Energy fed into the grid'].sum() / 1000), 2)
    SaleEnergy = round((Energy_intothegrid * 50.1), 2)

    # # Costospecifico_(impianto + installazione) [€/kWp]
    # if Potenza_installata < 10:
    #     # EPC = 1186.06 * (1 + 0.08)
    #     # TPC = EPC * (1 + 0.2)
    #     # Costospecifico = TPC * (1 + 0.2)
    #     Costospecifico = 1186.06
    #
    # elif 10 <= Potenza_installata <= 1000:
    #     # EPC = 934.16 * (1 + 0.08)
    #     # TPC = EPC * (1 + 0.2)
    #     # Costospecifico = TPC * (1 + 0.2)
    #     Costospecifico = 934.16
    # elif Potenza_installata > 1000:
    #     # EPC = 683.77 * (1 + 0.08)
    #     # TPC = EPC * (1 + 0.2)
    #     # Costospecifico = TPC * (1 + 0.2)
    #     Costospecifico = 683.77

        # Costo_investimento del membro della comunitá[€]
    Costo_investimento = info_member.iloc[0]['Investment [EUR]']

    # Costi O&M
    # RESIDENZIALE	2-10 kWp	17.79	€/kW/anno
    # COMMERCIALE	10 kWp-1 MWp	14.82	€/kW/anno
    # UTILITY SCALE	>1 MWp	11.01	€/kW/anno
    # Costospecifico_(O&m) [€/kWp]
    if Potenza_installata < 10:
        CostospecificoOM = 17.79
    elif 10 <= Potenza_installata <= 1000:
        CostospecificoOM = 14.82
    elif Potenza_installata > 1000:
        CostospecificoOM = 11.01

        # Costo_O&M del membro della comunitá[€/anno]
    Costo_OM = Potenza_installata * CostospecificoOM

    # ______________________________________________________________________________
    # PREZZO ENERGIA ELETTRICA VENDUTA ALLA RETE [€/MWh]
    # RITIRO DEDICATO	Impianti di qualsiasi potenza		52.35	€/MWh
    # PREZZI MINIMI GARANTITI	Impianti con potenza nominale fino a 100 kW + possono produrre al massimo 1500 MWh/anno		50.1 €/MWh
    if Potenza_installata <= 100:
        Prezzo_venditaRete = 50.1
    else:
        Prezzo_venditaRete = 52.35

    # Ricavi da vendita energia elettrica [€/anno]
    Ricavi_immissione_into = Energy_intothegrid * Prezzo_venditaRete

    # COSTO MEDIO ENERGIA ELETTRICA PRELEVATA DALLA RETE [€/MWh]
    if pd.isna(info_member.iloc[0]['Average energy cost [EUR/MWh]']) == True:
        Costo_energiadaRete = 0
    else:
        Costo_energiadaRete = info_member.iloc[0]['Average energy cost [EUR/MWh]']

    # Risparmio per autoconsumo [€/anno]
    Risparmio_realself = Energy_SelfCons * Costo_energiadaRete

    # Anni
    index = [*range(0, n_years + 1)]

    # Investimenti
    inv = [0] * (n_years + 1)
    inv[0] = -(Costo_investimento)

    # vendita energia in rete
    riceneprod = [Ricavi_immissione_into] * (n_years + 1)
    riceneprod[0] = 0

    # risparmio energia autoconsumata(non acquistata)
    rispself = [Risparmio_realself] * (n_years + 1)
    rispself[0] = 0

    # ricavo incentivo GSE
    ricGSE = [GSE_Incentive_member] * (n_years + 1)
    ricGSE[0] = 0

    Ricavi_totali = Risparmio_realself + Ricavi_immissione_into + GSE_Incentive_member
    ric = [Ricavi_totali] * (n_years + 1)
    ric[0] = 0

    # bonus 50%
    if info_member['Bonus 50%'].iloc[0] == True:
        if Costo_investimento < 96000:
            Importodetraibile = Costo_investimento / 2
            Detrazione_annua = Importodetraibile / 10
        else:
            Importodetraibile = 96000
            Detrazione_annua = Importodetraibile / 10
    else:
        Detrazione_annua = 0




    Ammortamento = (-Costo_investimento) / n_years
    amm = [Ammortamento] * (n_years + 1)
    amm[0] = 0

    detr = [Detrazione_annua] * (10 + 1)
    detr[0] = 0
    detr2 = [0] * (10)
    detrtot = detr + detr2

    OeM = (-Costo_OM)
    oem = [OeM] * (n_years + 1)
    oem[0] = 0

    zipped_lists = zip(ric, amm, detrtot, oem)
    ris = [x + y + z + i for (x, y, z, i) in zipped_lists]

    aliquota_imposte = 0.29
    imp = [- x * aliquota_imposte for x in riceneprod]

    CostoPartecipazione = (-10)
    costo = [CostoPartecipazione] * (n_years + 1)
    costo[0] = 0

    df_CASHFLOW = pd.DataFrame(list(zip(index, inv, riceneprod, rispself, ricGSE, ric, amm, detrtot, oem, ris, imp, costo)),
                               columns=['Anno', 'Investimento', 'Ricavi energia venduta alla rete',
                                        'Risparmi per autoconsumo', 'Ricavi incentivo GSE', 'Ricavi totali',
                                        'Ammortamento', 'Detrazioni', 'O&M', 'Risultato pre imposte', 'Imposte','Costo partecipazione comunitá'])
    df_CASHFLOW['Flusso di cassa netto'] = df_CASHFLOW['Risultato pre imposte'] + df_CASHFLOW['Imposte'] + df_CASHFLOW['Costo partecipazione comunitá']
    df_CASHFLOW.at[0, 'Flusso di cassa netto'] = -(Costo_investimento)

    Tassodisconto_i = 0.05

    df_CASHFLOW['Flusso di cassa netto attualizzato'] = df_CASHFLOW['Flusso di cassa netto'] / (1 + Tassodisconto_i) ** \
                                                        df_CASHFLOW['Anno']
    df_CASHFLOW.at[0, 'Flusso di cassa netto attualizzato'] = -(Costo_investimento)

    # df_CASHFLOW = df_CASHFLOW.set_index('Anno')

    df_CASHFLOW['VAN'] = df_CASHFLOW['Flusso di cassa netto attualizzato'].cumsum()

    economics_graph=go.Figure(
        data=[
            go.Bar(
                x=df_CASHFLOW["Anno"],
                y=df_CASHFLOW["Ricavi energia venduta alla rete"],
                name="Ricavi energia venduta alla rete",
                marker_color='palegoldenrod'
            ),
            go.Bar(
                x=df_CASHFLOW["Anno"],
                y=df_CASHFLOW["Risparmi per autoconsumo"],
                name="Risparmi per autoconsumo",
                marker_color='yellow'
            ),
            go.Bar(
                x=df_CASHFLOW["Anno"],
                y=df_CASHFLOW["Ricavi incentivo GSE"],
                name="Ricavi incentivo GSE",
                marker_color='gold'
            ),
            go.Bar(
                x=df_CASHFLOW["Anno"],
                y=df_CASHFLOW["Investimento"],
                name="Investimento",
                marker_color='darkblue'
            ),
            go.Bar(
                x=df_CASHFLOW["Anno"],
                y=df_CASHFLOW["Imposte"],
                name="Imposte",
                marker_color='royalblue'
            ),
            go.Bar(
                x=df_CASHFLOW["Anno"],
                y=df_CASHFLOW["Costo partecipazione comunitá"],
                name="Costo partecipazione comunitá",
                marker_color='steelblue'
            ),
            go.Scatter(
                x=df_CASHFLOW["Anno"],
                y= df_CASHFLOW['VAN'],
                mode='lines+markers',
                name='VAN')
        ],
        # layout=dict(template='none'),
        layout = dict(template='simple_white')
       )
    economics_graph.update_xaxes(range=[-0.5, 20.5])

    # Change the bar mode
    economics_graph.update_layout(barmode='stack')
    economics_graph.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1")
    economics_graph.update_layout(
        title=dict(
            text='<b>Flussi di cassa attualizzati</b>',
            x=0.5,
            # y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#000000')),
        xaxis=dict(
            title='Year',
            titlefont_size=16,
            tickfont_size=14,
        ),
        yaxis=dict(
            title='Flussi di cassa attualizzati [EUR]',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend_x=pos_x,
        legend_y=pos_y
        )

    return economics_graph


if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False,dev_tools_props_check=False)
