import os
import json
import pandas as pd
import plotly.io as pio
from dash import Dash, html, dash_table, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_ag_grid as dag


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
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Page 3", href="/page-3"),
                    dbc.DropdownMenuItem("Page 4", href="/page-4"),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
        ],
        brand=logo(),
        brand_href="/",
        color="primary",
        dark=True,
    )
    return navbar


def dashboard(df, column_settings):

    layout = dbc.Row([

        dashboard_sidebar(df),
        datatable(df, column_settings),

    ], style={"height": "100vh", "width": "100vw", "margin-left": "0px"})

    return layout


def dashboard_sidebar(df):

    layout = html.Div(
        [
        html.Div(
            [
            html.Button(
                children=["<<",
                          html.Img(src='/assets/filter_icon.png', style={'height': '25px', 'width': 'auto'})
                          ],
                id="collapse-dashboard-sidebar-button", n_clicks=0, className="filter-button",),
            ], style={"float": "right"}),

        html.Div(
            [
            dashboard_filters(df),
            html.Div(
                [
                dbc.Button(children="Download as .csv",
                           id="download-button"),
                dcc.Download(id="download-database"),

                dbc.Checklist(id="include-backend-columns-in-download-button",
                              options=[{"label": "Include back-end columns (not working yet)", "value": "include"}],
                              value=[]
                              ),
                ], style={"text-align": "center"})

            ], id="dashboard-sidebar-content", style={"padding-top": "10px"})

        ], id="dashboard-sidebar", className="sidebar-expanded")

    return layout


def dashboard_filters(df):

    layout = html.Div(
    [
        # Study Type
        html.Div(
        [
            dcc.Dropdown(
                id='study-type-dropdown',
                placeholder='Study Type',
                options=[{'label': i, 'value': i} for i in df['study_type'].unique()],
                value=[],
                clearable=True,
                multi=True,
                className='small-dropdown',
            ),
        ],),

        # Drug
        html.Div(
        [
            dcc.Dropdown(
                id='drug-dropdown',
                placeholder='Drug',
                options=[{'label': i, 'value': i} for i in df['drug'].unique()],
                value=[],
                clearable=True,
                multi=True,
                className='small-dropdown',
            ),
        ],),

        # Disease/Condition Indicated
        html.Div(
        [
            dcc.Dropdown(
                id='disease-dropdown',
                placeholder='Disease/Condition Indicated',
                options=[{'label': i, 'value': i} for i in df['disease_condition'].unique() if len(str(i))<50],
                value=[],
                clearable=True,
                multi=True,
                className='small-dropdown',
            ),
        ],),

        # Gestational Age
        html.Div(
        [
            html.Div(["Gestational Age:"]),
            dcc.RangeSlider(
                id="gest-age-range-slider",
                min=-10,
                max=60,
                step=1,
                value=[-10, 60],  # "Snapping" values
                marks={
                    -10: {"label": "Non-Pregnant", "style": {"transform": "rotate(-90deg) translate(-40px, -40px)", "white-space": "nowrap"}},
                    0: {"label": "0"},
                    14: {"label": "T1"},
                    28: {"label": "T2"},
                    40: {"label": "T3"},
                    50: {"label": "Delivery", "style": {"transform": "rotate(-90deg) translate(-20px, -20px)", "white-space": "nowrap"}},
                    60: {"label": "Postpartum", "style": {"transform": "rotate(-90deg) translate(-30px, -30px)", "white-space": "nowrap"}},
                },
                tooltip={"placement": "top", "always_visible": False}
            ),
        ],),
    ], id="dashboard_filters", style={"height": "100%", "margin-top":"25px", "padding-bottom": "100px"})

    return layout


def datatable(df, column_settings):

    layout = html.Div([
                        dash_table.DataTable(
                            id='table',

                            # columns=[{"name": i, "id": i} for i in df.columns],  # This creates an ID for each column so that I can call them later (eg. define column width)
                            # data=df.to_dict('records'), page_size=20,



                            # columns=[{"name": i, "id": i} for i in df.columns[20:40]],  # This creates an ID for each column so that I can call them later (eg. define column width)

                            columns=column_settings,
                            data=df[[col["id"] for col in column_settings]].to_dict('records'),

                            page_size=20,
                            style_table={'overflowX': 'auto'},  # Allows horizontal scrolling
                            style_cell_conditional=[{'if': {'column_id': 'pmid'},
                                                     'width': 1000}],  # Set initial width of Reference column
                            style_cell={'overflow':'hidden', 'textOverflow':'ellipsis','maxWidth':500},
                            editable=False,
                            # column_selectable="single",
                            sort_action="native",
                            row_selectable="multiple",
                            filter_action="native",
                            page_action="native",
                        )], id="table_col")

    return layout


def home_page():
    layout = html.H1(["This is the home page"])

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

    ], style={"height": "100vh", "width": "100vw", "margin-left": "0px"})

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


def ag_grid_layout(df):

    layout = html.Div(
    [
        # Filter dropdowns
        html.Div(
        [
            # Study Type
            html.Div(
            [
                dcc.Dropdown(
                    id='study-type-dropdown',
                    placeholder='Study Type',
                    options=[{'label': i, 'value': i} for i in df['Study Type'].unique()],
                    value=[],
                    clearable=True,
                    multi=True,
                    className='small-dropdown',
                ),
            ],),

            # Drug
            html.Div(
            [
                dcc.Dropdown(
                    id='drug-dropdown',
                    placeholder='Drug',
                    options=[{'label': i, 'value': i} for i in df['Drug'].unique()],
                    value=[],
                    clearable=False,
                    multi=True,
                    className='small-dropdown',
                ),
            ],),

            # Option 3
            html.Div(
            [
                dcc.Dropdown(
                    id='drug-dropdown-2',
                    placeholder='Option 3',
                    options=[{'label': 'Option 1', 'value': 'Option 1'}],
                    value=[],
                    clearable=False,
                    multi=True,
                    className='small-dropdown',
                ),
            ],),

        ],
            style={'width': '100%', 'display': 'flex', 'margin-bottom': '40px'}),

        # Actual Data Table
        html.Div([
            dag.AgGrid(
                id='table',
                rowData=df.to_dict("records"),
                columnDefs=[{"field": i} for i in df.columns],
                dashGridOptions={'pagination': True}
            )], )
    ],
)

    # @callback(
    #     Output('table', 'data'),
    #     [Input('study-type-dropdown', 'value'), Input('drug-dropdown', 'value')]
    # )
    # def update_table(selected_study_types, selected_drugs):
    #     filtered_df = df.copy()
    #     if selected_study_types:
    #         filtered_df = filtered_df[filtered_df['Study Type'].isin(selected_study_types)]
    #     if selected_drugs:
    #         filtered_df = filtered_df[filtered_df['Drug'].isin(selected_drugs)]
    #     return filtered_df.to_dict('records')
    #
    # return layout


# def ag_grid_layout(df):
#
#     layout = html.Div([
#         html.Div(children='Drug:'),
#         dcc.Dropdown(
#             id='drug-dropdown',
#             options=[{'label': 'Any', 'value': 'Any'}] + [{'label': i, 'value': i} for i in df['Drug'].unique()[:100]],
#             value='Any',
#             clearable=False,
#         ),
#
#         dag.AgGrid(
#             id='table',
#             rowData=df.to_dict("records"),
#             columnDefs=[{"field": i} for i in df.columns],
#             dashGridOptions={'pagination': True}
#             )
#     ])
#
#     @callback(
#         Output("table", "rowData"),
#         [Input("drug-dropdown", 'value')]
#     )
#     def update_table(selected_drug):
#         filtered_df = df.copy()
#         if selected_drug != 'Any':
#             filtered_df = filtered_df[filtered_df['Drug'] == selected_drug]
#         return filtered_df.to_dict('records')
#
#     app.run(debug=True)
