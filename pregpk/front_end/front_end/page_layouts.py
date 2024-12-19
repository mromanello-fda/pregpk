import os
import json
import math
import pandas as pd
import plotly
import plotly.io as pio
import plotly.express as px
from dash import Dash, html, dash_table, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

# TODO: Look at fluid=True argument in divs and other dbc/Dash components
# TODO: Look at dbc.Container instead of div?? Supposedly has several benefits


def logo():

    l = html.H1([
        html.Span('Preg', style={'color': 'white'}),
        'PK'
    ], style={'color': 'black'})

    return l


def get_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("PK Dashboard", href="/pk_dashboard")),
            dbc.NavItem(dbc.NavLink("Plots", href="/plots")),
            dbc.NavItem(dbc.NavLink("About Us", href="about-us")),
            dbc.NavItem(dbc.NavLink("Contact Us", href="contact")),
        ],
        brand=logo(),
        brand_href="/",
        color="primary",
        dark=True,
        style={
            "position": "fixed",
            "top": 0,
            "width": "100%",
            "zIndex": 1000,
        }
    )
    return navbar


def dashboard(df, column_settings, dropdowns):

    layout = html.Div(
                [
                    dashboard_sidebar(df, dropdowns),
                    dashboard_data_column(df, column_settings)
                ],
                className="dashboard-container",
    )

    return layout


def dashboard_sidebar(df, dropdowns):

    # TODO: Values for sliders (min, max, unique, etc.) should not have to be computed every time this funciton
    #  is called. In future, go through every function in layout that should only be called once and do so before
    #  the site is built (and then import values), maybe do it with __init__.py?

    layout = html.Div(
        [
            html.Div(
                [
                    html.Button("\u2630",
                                id="collapse-dashboard-sidebar-button", n_clicks=0,
                                className="blended-button",
                                style={"float": "right", "font-size": "40px", "color": "white"}
                                ),
                ],
                style={"width": "100%", "overflow": "hidden", "min-height": "62px", "clear": "both"}
            ),
            html.Div(
                [
                    # Drug group
                    html.Button(
                                n_clicks=1,
                                id="collapse-button-drug-filters",
                                className="blended-button full-width-menu",
                                ),
                    dbc.Collapse(
                        [
                            # Name
                            html.Div(
                                [
                                    "By drug name:",
                                    dcc.Dropdown(
                                        id='drug-dropdown',
                                        placeholder='Drug',
                                        options=[{'label': key, 'value': val} for key, val in
                                                 dropdowns["drug"].items()],
                                        value=[],
                                        clearable=True,
                                        multi=True,
                                        className='small-dropdown',
                                    ),
                                ],
                                className="filter-item"
                            ),

                            # ATC Code
                            html.Div(
                                [
                                    "By ATC Code:",
                                    dcc.Dropdown(
                                        placeholder='ATC Code',
                                        # options=[{'label': i, 'value': i} for i in df['drug'].unique()],
                                        options=[],
                                        value=[],
                                        clearable=True,
                                        multi=True,
                                        className='small-dropdown',
                                    ),
                                ],
                                className="filter-item"
                            ),

                            # CAS Number
                            html.Div(
                                [
                                    "By CAS Number:",
                                    dcc.Dropdown(
                                        placeholder='CAS Code',
                                        # options=[{'label': i, 'value': i} for i in df['drug'].unique()],
                                        options=[],
                                        value=[],
                                        clearable=True,
                                        multi=True,
                                        className='small-dropdown',
                                    ),
                                ],
                                className="filter-item"
                            )
                        ],
                        id="drug-filters-collapse",
                        class_name="filter-group"
                    ),

                    # Disease/Condition
                    html.Button(
                                n_clicks=1,
                                id="collapse-button-disease-filters",
                                className="blended-button full-width-menu",
                    ),
                    dbc.Collapse(
                        [
                            # Name
                            html.Div(
                                [
                                    "By disease/condition name:",
                                    dcc.Dropdown(
                                        id='disease-dropdown',
                                        placeholder='Disease/Condition Indicated',
                                        options=[{'label': i, 'value': i} for i in df['disease_condition'].unique() if
                                                 len(str(i)) < 50],
                                        value=[],
                                        clearable=True,
                                        multi=True,
                                        className='small-dropdown',
                                    ),
                                ],
                                className="filter-item"
                            ),

                            # ICD-10 Code
                            html.Div(
                                [
                                    "By ICD-10 Code:",
                                    dcc.Dropdown(
                                        placeholder='ICD-10 Code',
                                        options=[],
                                        value=[],
                                        clearable=True,
                                        multi=True,
                                        className='small-dropdown',
                                    ),
                                ],
                                className="filter-item"
                            ),

                        ],
                        id="disease-filters-collapse",
                        class_name="filter-group"
                    ),

                    # Gestational Age
                    html.Button(
                        n_clicks=1,
                        id="collapse-button-gest-age-filters",
                        className="blended-button full-width-menu",
                    ),
                    dbc.Collapse(
                        [
                            html.Div(
                                [
                                    "By range:",
                                    dcc.RangeSlider(
                                        id="gest-age-range-slider",
                                        min=-10,
                                        max=60,
                                        step=1,
                                        value=[-10, 60],  # "Snapping" values
                                        marks={
                                            -10: {"label": "Non-Pregnant",
                                                  "style": {"transform": "rotate(-90deg) translate(-40px, -40px)",
                                                            "white-space": "nowrap",
                                                            "color": "white"}},
                                            0: {"label": "0",
                                                "style": {"color": "white"}},
                                            13: {"label": "T1",
                                                 "style": {"color": "white"}},
                                            27: {"label": "T2",
                                                 "style": {"color": "white"}},
                                            40: {"label": "T3",
                                                 "style": {"color": "white"}},
                                            50: {"label": "Delivery",
                                                 "style": {"transform": "rotate(-90deg) translate(-20px, -20px)",
                                                           "white-space": "nowrap",
                                                           "color": "white"}},
                                            60: {"label": "Postpartum",
                                                 "style": {"transform": "rotate(-90deg) translate(-30px, -30px)",
                                                           "white-space": "nowrap",
                                                           "color": "white"}},
                                        },
                                        tooltip={"placement": "top", "always_visible": False},
                                    ),
                                ],
                                className="filter-item",
                                style={"margin-bottom": "75px"},
                            ),
                            html.Div(
                                [
                                    "By trimester:",
                                    dbc.Checklist(
                                        options=[
                                            {"label": "Non-Pregnant", "value": 0},
                                            {"label": "1st Trimester", "value": 1},
                                            {"label": "2nd Trimester", "value": 2},
                                            {"label": "3rd Trimester", "value": 3},
                                            {"label": "Delivery", "value": 4},
                                            {"label": "Postpartum", "value": 5}
                                        ],
                                        value=[0, 1, 2, 3, 4, 5],
                                        id="gest-age-checklist",
                                    ),
                                ],
                                className="filter-item"
                            )

                        ],
                        id="gest-age-filters-collapse",
                        class_name="filter-group"
                    ),

                    # Source
                    html.Button(
                        n_clicks=1,
                        id="collapse-button-source-filters",
                        className="blended-button full-width-menu",
                    ),
                    dbc.Collapse(
                        [
                            html.Div(
                                [
                                    "Year of Publication:",
                                    dcc.RangeSlider(
                                        id="pub-year-range-slider",
                                        min=df["pub_year"].min(),
                                        max=df["pub_year"].max(),
                                        step=1,
                                        value=[df["pub_year"].min(), df["pub_year"].max()],  # "Snapping" values
                                        marks={val: {"label": f"{val}",
                                                     "style": {"color": "white"}
                                                     } for val in
                                               [dec * 10 for dec in range(math.ceil((df["pub_year"].min() + 1) / 10),
                                                                          math.floor(
                                                                              (df["pub_year"].max() - 1) / 10) + 1)]
                                               # +1 and -1 to make sure values not repeated
                                               },
                                        tooltip={"placement": "top", "always_visible": False}
                                    ),
                                ],
                                className="filter-item"
                            ),

                            html.Div(
                                [
                                    "Study Type:",
                                    dcc.Dropdown(
                                        id='study-type-dropdown',
                                        placeholder='Study Type',
                                        options=[{'label': i, 'value': i} for i in df['study_type'].unique()],
                                        value=[],
                                        clearable=True,
                                        multi=True,
                                        className='small-dropdown',
                                    )
                                ],
                                className="filter-item"
                            )
                        ],
                        id="source-filters-collapse",
                        class_name="filter-group"
                    ),

                    # Plots
                    html.Button(
                        n_clicks=1,
                        id="collapse-button-plot-options",
                        className="blended-button full-width-menu",
                    ),
                    dbc.Collapse(
                        [
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id='plot-xaxis-dropdown',
                                        placeholder='Plot against:',
                                        options=[{'label': "Dose", 'value': "dose"},
                                                 {'label': "Gestational Age", 'value': "gestational_age"}],
                                        # value=[],
                                        clearable=True,
                                        multi=False,
                                        className='small-dropdown',
                                    ),
                                    dcc.Dropdown(
                                        id='plot-groupby-dropdown',
                                        placeholder='Group data by: (under construction)',
                                        options=[{'label': "Dose", 'value': "dose"},
                                                 {'label': "Gestational Age", 'value': "gestational_age"}],
                                        # value=[],
                                        clearable=True,
                                        multi=False,
                                        className='small-dropdown',
                                    )
                                ],
                                className="filter-item"
                            )
                        ],
                        id="plot-options-collapse",
                        class_name="filter-group"
                    ),

                    html.Button(
                        n_clicks=1,
                        id="collapse-button-download-options",
                        className="blended-button full-width-menu"
                    ),
                    dbc.Collapse(
                        [
                            html.Div(
                                [
                                    dbc.Checklist(id="include-backend-columns-in-download-button",
                                                  options=[
                                                      {"label": "Include back-end columns (not working yet)", "value": "include"}],
                                                  ),
                                    dbc.Button("Download as .csv",
                                               id="download-button",
                                               ),
                                    dcc.Download(id="download-database"),
                                ],
                                className="filter-item"
                            ),
                        ],
                        id="download-options-collapse",
                        class_name="filter-group"
                    ),

                    # html.Div(
                    #     style={"text-align": "center", "padding-top": "100px"}
                    # )

                ],
                id="dashboard-sidebar-content",
                className="sidebar-content"
            )
        ],
        id="dashboard-sidebar",
        className="sidebar-expanded",
    )

    return layout


def dashboard_data_column(df, column_settings):

    layout = html.Div([
        datatable(df, column_settings),
        # data_ag_grid(df, column_settings),
        dashboard_plot_div(),
        # dashboard_plots(),
    ],
        id="data_col",
    )

    return layout


def datatable(df, column_settings):

    layout = html.Div([
                        dash_table.DataTable(
                            id='table',

                            columns=column_settings,
                            data=df[[col["id"] for col in column_settings]].fillna("").to_dict('records'),

                            page_size=20,
                            style_table={'overflowX': 'auto'},  # Allows horizontal scrolling
                            style_cell_conditional=[
                                {'if': {'column_id': 'row_id'}, 'display': 'None'},  # Important to keep in data variable

                                {'if': {'column_id': 'pmid_hyperlink'},
                                 'width': 1000,
                                 },  # Actual formatting
                            ],
                            style_cell={'overflow': 'hidden',
                                        'textOverflow': 'ellipsis',
                                        'maxWidth': 500,
                                        },

                            editable=False,
                            # column_selectable="single",
                            sort_action="custom",
                            row_selectable="multiple",
                            filter_action="native",
                            page_action="native",
                        )], id="table_div")

    return layout


def dashboard_content(df, column_settings):

    layout = html.Div([
        datatable(df, column_settings),
    ])

    return layout


def dashboard_plots():

    layout = html.Div(
        [
            dcc.Graph(id="dashboard-plot"),
        ]
    )

    return layout


def dashboard_plot_options_button():

    l = html.Div(
        [
            dcc.Dropdown(
                id='plot-xaxis-dropdown',
                placeholder='Plot against:',
                options=[{'label': "Dose", 'value': "dose"},
                         {'label': "Gestational Age", 'value': "gestational_age"}],
                # value=[],
                clearable=True,
                multi=False,
                className='small-dropdown',
            ),
            dcc.Dropdown(
                id='plot-groupby-dropdown',
                placeholder='Group data by: (under construction)',
                options=[{'label': "Dose", 'value': "dose"},
                         {'label': "Gestational Age", 'value': "gestational_age"}],
                # value=[],
                clearable=True,
                multi=False,
                className='small-dropdown',
            )
        ]
    )

    return l


def dashboard_plot_div():
    layout = html.Div(
        [
            # dashboard_plot_options_button(),
            dashboard_plots(),
        ]
    )

    return layout


def plot_sidebar():

    sb = html.Div(
        [
        html.Div(
            [
            html.Button(
                children=["<<",],
                id="collapse-plot-sidebar-button", n_clicks=0, className="filter-button",),
            ], style={"float": "right"}
        ),

        ], id="plot-sidebar", className="sidebar-expanded")

    return sb


def plot_page():

    with open(os.path.join('plots', 'all_fig_info.json'), 'r') as f:
        all_figs = json.load(f)

    for i_fig_dict in all_figs:
        i_fig_dict["plotly_fig_obj"] = pio.from_json(json.dumps(i_fig_dict["plotly_fig_obj"]))

    layout = dbc.Row([
        plot_sidebar(),
        html.Div([dcc.Graph(figure=i_fig["plotly_fig_obj"]) for i_fig in all_figs],
                 id="plot_col", className="page-collapsed")

    ], style={"height": "100%", "width": "100%", "margin-left": "0px"})

    return layout


def under_construction_page():
    layout = html.Div(
        [
            html.H1(["Page under construction"]),
            html.H1(["🚧 🚧 🚧 🚧"]),
        ]
    )

    return layout


def error_404_page():
    layout = html.H1(["404: Page not found."])

    return layout


# def data_ag_grid(df, column_settings):
#
#     layout = html.Div(
#         [
#             dag.AgGrid(
#                 id='table',
#                 rowData=df[[col["id"] for col in column_settings]].to_dict("records"),
#                 columnDefs=[{"field": i} for i in df[[col["id"] for col in column_settings]].columns],
#                 dashGridOptions={'pagination': True}
#             )
#         ],
#     )
#
#     return layout
