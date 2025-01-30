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
            dbc.NavItem(dbc.NavLink("PK Dashboard", href="/pk-dashboard")),
            dbc.NavItem(dbc.NavLink("About This Data", href="/about-this-data")),
            dbc.NavItem(dbc.NavLink("About Us", href="/about-us")),
            dbc.NavItem(dbc.NavLink("Contact/Cite Us", href="/contact-cite-us")),
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
                className="page dashboard-container",
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

    layout = html.Div(
                [
                    plot_sidebar(),
                    html.Div([dcc.Graph(figure=i_fig["plotly_fig_obj"]) for i_fig in all_figs],
                             id="plot_col", className="page-collapsed")
                ],
                className="page dashboard-container",
    )

    return layout


def contact_us_page():

    layout = html.Div(
        ["Hello contact"],
        className="page",
    )

    return layout


def about_us_page():

    layout = html.Div(
        [
            profile(
                "assets/people/kiara_fairman.jpg",
                "Kiara Fairman, MS, PharmD",
                "Divison of Biochemical Toxicity, NCTR",
                "Principal Investigator",
                "Dr. Fairman is a staff fellow at FDA’s National Center for Toxicological Research (NCTR). She "
                "previously served as an Oak Ridge Institute for Science and Education (ORISE) postdoctoral fellow "
                "at NCTR from 2019–2021, where she worked on physiologically-based pharmacokinetic modeling tools for "
                "regulatory decision making in pregnancy and other life stages. She received a Doctor of Pharmacy "
                "degree from the University of North Texas System College of Pharmacy in Fort Worth, Texas. She holds "
                "a Certificate in Regulatory Science from the University of Arkansas for Medical Sciences; a Master "
                "of Science degree in biological sciences—chemistry track from the University of Texas Southwestern "
                "Medical Center in Dallas, Texas; and a bachelor’s degree in chemistry from Alabama State University. "
                "Dr. Fairman has attended and presented at various conferences and annual meetings in the areas of "
                "toxicology, clinical pharmacology, pharmacy, and chemistry."
            ),

            profile(
                "assets/people/miao_li.jpg",
                "Miao Li, PhD, DABT",
                "Office of Cosmetics and Colors, CFSAN",
                "Principal Investigator",
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
                "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                "culpa qui officia deserunt mollit anim id est laborum."
            ),

            profile(
                "assets/people/blessy_george.jpg",
                "Blessy George, PharmD, PhD",
                "Office of New Drugs, CDER",
                "Principal Investigator",
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
                "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                "culpa qui officia deserunt mollit anim id est laborum."
            ),

            profile(
                "assets/people/joshua_xu.jpg",
                "Joshua Xu, PhD",
                "Division of Bioinformatics and Biostatistics, NCTR",
                "Principal Investigator",
                "After graduating with a Ph.D. in electrical engineering from Texas A&M University in 1999, Dr. Xu "
                "worked as a senior software engineer for a congressionally-funded mobile telemedicine program at the "
                "Texas Center for Applied Technology, an R&D center of the Texas A&M University System. In this "
                "position, he designed and developed many vital modules through software development and hardware "
                "integration. In 2007, he joined ICF International to work as an onsite contractor for the National "
                "Center for Toxicological Research. Dr. Xu’s primary responsibilities included:  1) data analysis, "
                "2) bioinformatics method development, and 3) design and development of bioinformatics tools and "
                "systems to manage and analyze genomics data."
            ),

            profile(
                "assets/people/yifan_zhang.jpg",
                "Yifan Zhang, PhD",
                "Division of Bioinformatics and Biostatistics, NCTR",
                "Principal Investigator",
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
                "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                "culpa qui officia deserunt mollit anim id est laborum."
            ),

            profile(
                "assets/people/miguel_romanello.jpg",
                "Miguel Romanello Joaquim, MS",
                "Divison of Biochemical Toxicity, NCTR",
                "Developer, ORISE Fellow",
                "Born in Brazil, Bachelors from Notre Dame, Masters from UPenn, lives in Little Rock, working as an "
                "ORISE Fellow since January 2024",
            ),

            profile(
                "assets/people/emily_ciborek.jpg",
                "Emily Ciborek, PharmD",
                "--",
                "--",
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
                "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                "culpa qui officia deserunt mollit anim id est laborum."
            ),

        ],
        className="page",
    )
    return layout


def profile(headshot_path, name_text, affiliation_text, role_text, bio_text):

    layout = html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src=headshot_path,
                        className="profile-headshot"
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.A(
                                    html.Img(
                                        src="assets/icons/envelope-at-fill.svg",
                                        style={"width": "100%"}
                                    ),
                                    href="mailto:someone@example.com",
                                    target="_blank",
                                ),
                                className="profile-link-icon"
                            ),
                            html.Div(
                                html.A(
                                    html.Img(
                                        src="assets/icons/orcid.svg",
                                        style={"width": "100%"}
                                    ),
                                    href="https://orcid.org",
                                    target="_blank",
                                ),
                                className="profile-link-icon"
                            ),
                            html.Div(
                                html.A(
                                    html.Img(
                                        src="assets/icons/github.svg",
                                        style={"width": "100%"}
                                    ),
                                    href="https://github.com/mromanello-fda",
                                    target="_blank",
                                ),
                                className="profile-link-icon"
                            ),
                            html.Div(
                                html.A(
                                    html.Img(
                                        src="assets/icons/linkedin.svg",
                                        style={"width": "100%"}
                                    ),
                                    href="https://linkedin.com/mromanello",
                                    target="_blank",
                                ),
                                className="profile-link-icon"
                            ),
                        ],
                        className="profile-links"
                    )
                ],
                className="profile-headshot-and-links"
            ),
            html.Div(
                [
                    html.Div(
                        name_text,
                        className="profile-name"),
                    html.Div(
                        affiliation_text,
                        className="profile-affiliation"
                    ),
                    html.Div(
                        role_text,
                        className="profile-role"
                    ),
                    html.Div(
                        bio_text,
                        className="profile-bio"
                    ),
                ],
                className="profile-text",
            ),
        ],
        className="profile",
    )

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
