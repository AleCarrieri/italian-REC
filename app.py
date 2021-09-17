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
import gendoc

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
    html.Br(),
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



if __name__ == '__main__':
    app.run_server(debug=False)
