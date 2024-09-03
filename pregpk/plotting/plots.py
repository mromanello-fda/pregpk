import os
import numpy as np
import pandas as pd
import pickle
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots
import plotly.io as pio
from pregpk import gen_utils, countries


class PlotlyFigFileHandler:
    def __init__(self):
        self._fig_list = []

    def add_fig(self, fig, fig_name):
        self._fig_list.append(
            {"name": fig_name,
             "plotly_fig_obj": fig}
        )
        return

    def save_all_figs_file(self, path):

        for i_fig_dict in self._fig_list:
            i_fig_dict["plotly_fig_obj"] = json.loads(pio.to_json(i_fig_dict["plotly_fig_obj"]))

        with open(path, "w") as fig_file_json:
            json.dump(self._fig_list, fig_file_json)

        return


def is_nan(val):

    if isinstance(val, str):
        return val == "nan"

    if isinstance(val, float):
        return np.isnan(val)

    if isinstance(val, int):
        return np.isnan(val)

    print(val)
    return


show_plots = False

# Open main file and column name indexes
with open("pkdb.pkl", "rb") as pkl_file:
    df = pickle.load(pkl_file)

with open(os.path.join("col_name_indexes", "ctr_to_col_name.json"), "r") as f:
    ctr_to_col_name = json.load(f)
with open(os.path.join("col_name_indexes", "lang_to_col_name.json"), "r") as f:
    lang_to_col_name = json.load(f)


# Plots
pk_params = ['auc', 'cl', 'c_max', 'c_min', 't_half', 't_max', 'other_pk_data']
for pkp in pk_params:
    new_col = f"has_{pkp}"
    df[new_col] = ~df[pkp].map(is_nan)

# Plot 1: General parameter meta-analysis
fig1_data = {i_pkp: {} for i_pkp in pk_params}
color_map = {"auc": "#F8766D",
             "cl": "#B79F00",
             "c_max": "#00BA38",
             "c_min": "#00BFC4",
             "t_half": "#A58AFF",
             "t_max": "#F564E3",
             "other_pk_data": "#619CFF",
             }
xlabel_map = {"auc": "AUC",
              "cl": "CL",
              "c_max": "$C_{max}$",
              "c_min": "$C_{min}$",
              "t_half": "$T_{1/2}$",
              "t_max": "$T_{max}$",
              "other_pk_data": "Single conc."}

for i_pkp in fig1_data:
    fig1_data[i_pkp]["n_dps"] = df[f"has_{i_pkp}"].sum()
    fig1_data[i_pkp]["n_pubs"] = len(df[df[f"has_{i_pkp}"]]['pmid'].unique())
    fig1_data[i_pkp]["n_drugs"] = len(df[df[f"has_{i_pkp}"]]['gsrs_unii'].unique())
    fig1_data[i_pkp]["color"] = color_map[i_pkp]
    fig1_data[i_pkp]['xlabel'] = xlabel_map[i_pkp]


fig1 = plotly.subplots.make_subplots(rows=1, cols=3,
                                     subplot_titles=("Datapoints", "Publications", "Drugs"))
for i_val_type, val_type in enumerate(["n_dps", "n_pubs", "n_drugs"], start=1):
    xord = sorted(
        list(fig1_data.keys()),
        key=lambda i: fig1_data[i][val_type],
        reverse=True,
        )
    for i_pkp in xord:
        fig1.add_trace(
            go.Bar(name=fig1_data[i_pkp]["xlabel"],
                   x=[fig1_data[i_pkp]["xlabel"]],
                   y=[fig1_data[i_pkp][val_type]],
                   marker_color=fig1_data[i_pkp]["color"],
                   legendgroup=fig1_data[i_pkp]["xlabel"],
                   showlegend=i_val_type == 1,  # Only true for one plot
                   text=[fig1_data[i_pkp][val_type]],
                   textposition="outside",
                   ),
            row=1, col=i_val_type
        )

fig1.update_layout(
    margin=dict(t=25, b=10, l=10, r=10),
    showlegend=True,
    legend=dict(
        x=1.00,
    )
)
fig1.update_xaxes(showticklabels=False)
if show_plots:
    fig1.show()


# Plot 2: General trimester meta-analysis
trimesters = ['tri_1', 'tri_2', 'tri_3', 'has_delivery_data', 'has_postpartum_data', 'total']
fig2_data = {i_tri: {} for i_tri in trimesters}
xlabel_map = {"tri_1": "Trimester I",
              "tri_2": "Trimester II",
              "tri_3": "Trimester III",
              "has_delivery_data": "Delivery",
              "has_postpartum_data": "Postpartum",
              "total": "Total",}
color_map = {"tri_1": "#F8766D",
             "tri_2": "#B79F00",
             "tri_3": "#00BA38",
             "has_delivery_data": "#00BFC4",
             "has_postpartum_data": "#619CFF",
             "total": "#F564E3",
             }

for i_tri in fig2_data:
    if i_tri == "total":
        fig2_data[i_tri]["n_dps"] = df[trimesters[:-1]].any(axis=1).sum()
        fig2_data[i_tri]["n_pubs"] = len(df[df[trimesters[:-1]].any(axis=1)]['pmid'].unique())
        fig2_data[i_tri]["n_drugs"] = len(df[df[trimesters[:-1]].any(axis=1)]['drug'].unique())
    else:
        fig2_data[i_tri]["n_dps"] = df[i_tri].sum()
        fig2_data[i_tri]['n_pubs'] = len(df[df[i_tri]]['pmid'].unique())
        fig2_data[i_tri]['n_drugs'] = len(df[df[i_tri]]['gsrs_unii'].unique())
    fig2_data[i_tri]["color"] = color_map[i_tri]
    fig2_data[i_tri]["xlabel"] = xlabel_map[i_tri]

fig2 = plotly.subplots.make_subplots(rows=1, cols=3,
                                     subplot_titles=("Datapoints", "Publications", "Drugs"))
for i_val_type, val_type in enumerate(["n_dps", "n_pubs", "n_drugs"], start=1):
    xord = trimesters
    for i_tri in xord:
        fig2.add_trace(
            go.Bar(name=fig2_data[i_tri]["xlabel"],
                   x=[fig2_data[i_tri]["xlabel"]],
                   y=[fig2_data[i_tri][val_type]],
                   marker_color=fig2_data[i_tri]["color"],
                   legendgroup=fig2_data[i_tri]["xlabel"],
                   showlegend=i_val_type == 1,  # Only true for one plot
                   text=[fig2_data[i_tri][val_type]],
                   textposition="outside",
                   ),
            row=1, col=i_val_type
        )

fig2.update_layout(
    margin=dict(t=25, b=10, l=10, r=10),
    showlegend=True,
    legend=dict(
        x=1.00,
    )
)
fig2.update_xaxes(showticklabels=False)
if show_plots:
    fig2.show()


# Plot of PK parameter metadata by decade
year_ranges = ((1944, 1969), (1970, 1979), (1980, 1989), (1990, 1999), (2000, 2009), (2010, 2019))
pk_params = ['auc', 'cl', 'c_max', 'c_min', 't_half', 't_max', 'other_pk_data']
fig3_data = {i_pkp: {} for i_pkp in pk_params}
color_map = {"auc": "#F8766D",
             "cl": "#B79F00",
             "c_max": "#00BA38",
             "c_min": "#00BFC4",
             "t_half": "#A58AFF",
             "t_max": "#F564E3",
             "other_pk_data": "#619CFF",
             }
xlabel_map = {"auc": "AUC",
              "cl": "CL",
              "c_max": "$C_{max}$",
              "c_min": "$C_{min}$",
              "t_half": "$T_{1/2}$",
              "t_max": "$T_{max}$",
              "other_pk_data": "Single conc."}

for i_pkp in fig3_data:
    fig3_data[i_pkp]["n_dps"] = {}
    fig3_data[i_pkp]["n_pubs"] = {}
    fig3_data[i_pkp]["n_drugs"] = {}

    for i_drange in year_ranges:
        drange_df = df[ (df['pub_year']>=i_drange[0]) & (df['pub_year']<=i_drange[1]) ]

        fig3_data[i_pkp]["n_dps"][i_drange] = drange_df[f"has_{i_pkp}"].sum()
        fig3_data[i_pkp]["n_pubs"][i_drange] = len(drange_df[drange_df[f"has_{i_pkp}"]]['pmid'].unique())
        fig3_data[i_pkp]["n_drugs"][i_drange] = len(drange_df[drange_df[f"has_{i_pkp}"]]['gsrs_unii'].unique())

    fig3_data[i_pkp]["color"] = color_map[i_pkp]
    fig3_data[i_pkp]['xlabel'] = xlabel_map[i_pkp]

fig3 = plotly.subplots.make_subplots(
    rows=3, cols=len(year_ranges),
    subplot_titles=tuple(f"{i[0]} - {i[1]}" for i in year_ranges),
    vertical_spacing=0.03,
    horizontal_spacing=0.03,
)
xord = pk_params
for iran, ran in enumerate(year_ranges, start=1):
    for i_pkp in xord:
        fig3.add_trace(
            go.Bar(
                name=fig3_data[i_pkp]["xlabel"],
                x=[fig3_data[i_pkp]["xlabel"]],
                y=[fig3_data[i_pkp]["n_dps"][ran]],
                marker_color=fig3_data[i_pkp]["color"],
                legendgroup=fig3_data[i_pkp]["xlabel"],
                text=[fig3_data[i_pkp]["n_dps"][ran]],
                textposition="outside",
                showlegend=iran == 1,
            ),
            row=1, col=iran,
        ),

        fig3.add_trace(
            go.Bar(
                name=fig3_data[i_pkp]["xlabel"],
                x=[fig3_data[i_pkp]["xlabel"]],
                y=[fig3_data[i_pkp]["n_drugs"][ran]],
                marker_color=fig3_data[i_pkp]["color"],
                legendgroup=fig3_data[i_pkp]["xlabel"],
                text=[fig3_data[i_pkp]["n_drugs"][ran]],
                textposition="outside",
                showlegend=False,
            ),
            row=2, col=iran,
        ),

        fig3.add_trace(
            go.Bar(
                name=fig3_data[i_pkp]["xlabel"],
                x=[fig3_data[i_pkp]["xlabel"]],
                y=[fig3_data[i_pkp]["n_pubs"][ran]],
                marker_color=fig3_data[i_pkp]["color"],
                legendgroup=fig3_data[i_pkp]["xlabel"],
                text=[fig3_data[i_pkp]["n_pubs"][ran]],
                textposition="outside",
                showlegend=False,
            ),
            row=3, col=iran,
        )

fig3.update_layout(
    margin=dict(t=25, b=10, l=10, r=10),
    showlegend=True,
    legend=dict(
        x=1.00,
    )
)
fig3.update_yaxes(title_text="Datapoints", row=1, col=1)
fig3.update_yaxes(title_text="Publications", row=2, col=1)
fig3.update_yaxes(title_text="Drugs", row=3, col=1)

for ir, i_y_ranges in enumerate([(0, 4000), (0, 150), (0, 200)], start=1):
    for ic in range(1, len(year_ranges)+1):
        fig3.update_xaxes(showticklabels=False, row=ir, col=ic)
        fig3.update_yaxes(range=i_y_ranges, row=ir, col=ic)

        if ic != 1:
            fig3.update_yaxes(showticklabels=False, row=ir, col=ic)

if show_plots:
    fig3.show()

# Plot of PK parameter metadata by decade
year_ranges = ((1944, 1969), (1970, 1979), (1980, 1989), (1990, 1999), (2000, 2009), (2010, 2019))
trimesters = ['tri_1', 'tri_2', 'tri_3', 'has_delivery_data', 'has_postpartum_data', 'total']
fig4_data = {i_tri: {} for i_tri in trimesters}
xlabel_map = {"tri_1": "Trimester I",
              "tri_2": "Trimester II",
              "tri_3": "Trimester III",
              "has_delivery_data": "Delivery",
              "has_postpartum_data": "Postpartum",
              "total": "Total",}
color_map = {"tri_1": "#F8766D",
             "tri_2": "#B79F00",
             "tri_3": "#00BA38",
             "has_delivery_data": "#00BFC4",
             "has_postpartum_data": "#619CFF",
             "total": "#F564E3",
             }

for i_tri in fig4_data:
    fig4_data[i_tri]["n_dps"] = {}
    fig4_data[i_tri]["n_pubs"] = {}
    fig4_data[i_tri]["n_drugs"] = {}

    for i_drange in year_ranges:
        drange_df = df[ (df['pub_year']>=i_drange[0]) & (df['pub_year']<=i_drange[1]) ]

        if i_tri == "total":
            fig4_data[i_tri]["n_dps"][i_drange] = drange_df[trimesters[:-1]].any(axis=1).sum()
            fig4_data[i_tri]["n_pubs"][i_drange] = len(drange_df[drange_df[trimesters[:-1]].any(axis=1)]['pmid'].unique())
            fig4_data[i_tri]["n_drugs"][i_drange] = len(drange_df[drange_df[trimesters[:-1]].any(axis=1)]['drug'].unique())
        else:
            fig4_data[i_tri]["n_dps"][i_drange] = drange_df[i_tri].sum()
            fig4_data[i_tri]['n_pubs'][i_drange] = len(drange_df[drange_df[i_tri]]['pmid'].unique())
            fig4_data[i_tri]['n_drugs'][i_drange] = len(drange_df[drange_df[i_tri]]['gsrs_unii'].unique())
        fig4_data[i_tri]["color"] = color_map[i_tri]
        fig4_data[i_tri]["xlabel"] = xlabel_map[i_tri]

fig4 = plotly.subplots.make_subplots(
    rows=3, cols=len(year_ranges),
    subplot_titles=tuple(f"{i[0]} - {i[1]}" for i in year_ranges),
    vertical_spacing=0.03,
    horizontal_spacing=0.03,
)
xord = trimesters
for iran, ran in enumerate(year_ranges, start=1):
    for i_tri in trimesters:
        fig4.add_trace(
            go.Bar(
                name=fig4_data[i_tri]["xlabel"],
                x=[fig4_data[i_tri]["xlabel"]],
                y=[fig4_data[i_tri]["n_dps"][ran]],
                marker_color=fig4_data[i_tri]["color"],
                text=[fig4_data[i_tri]["n_dps"][ran]],
                textposition="outside",
                showlegend=iran == 1,
            ),
            row=1, col=iran,
        )
        fig4.add_trace(
            go.Bar(
                name=fig4_data[i_tri]["xlabel"],
                x=[fig4_data[i_tri]["xlabel"]],
                y=[fig4_data[i_tri]["n_drugs"][ran]],
                marker_color=fig4_data[i_tri]["color"],
                text=[fig4_data[i_tri]["n_drugs"][ran]],
                textposition="outside",
                showlegend=False,
            ),
            row=2, col=iran,
        ),
        fig4.add_trace(
            go.Bar(
                name=fig4_data[i_tri]["xlabel"],
                x=[fig4_data[i_tri]["xlabel"]],
                y=[fig4_data[i_tri]["n_pubs"][ran]],
                marker_color=fig4_data[i_tri]["color"],
                text=[fig4_data[i_tri]["n_pubs"][ran]],
                textposition="outside",
                showlegend=False,
            ),
            row=3, col=iran,
        )
fig4.update_layout(
    margin=dict(t=25, b=10, l=10, r=10),
    showlegend=True,
    legend=dict(
        x=1.00,
    )
)
fig4.update_yaxes(title_text="Datapoints", row=1, col=1)
fig4.update_yaxes(title_text="Publications", row=2, col=1)
fig4.update_yaxes(title_text="Drugs", row=3, col=1)

for ir, i_y_ranges in enumerate([(0, 4500), (0, 200), (0, 300)], start=1):
    for ic in range(1, len(year_ranges)+1):
        fig4.update_xaxes(showticklabels=False, row=ir, col=ic)
        fig4.update_yaxes(range=i_y_ranges, row=ir, col=ic)

        if ic != 1:
            fig4.update_yaxes(showticklabels=False, row=ir, col=ic)

if show_plots:
    fig4.show()


# Plot of countries that published
ctrs_to_show = 20
col_name_to_ctr = gen_utils.invert_dict(ctr_to_col_name)

fig5_data = pd.DataFrame(
    index=ctr_to_col_name.keys(),
    columns=['single_country_publications', 'multiple_country_publications'],
)

for ctr, col_name in ctr_to_col_name.items():
    relevant_cols = ['pmid'] + list(col_name_to_ctr.keys())
    curr_ctr_pubs = df[df[col_name]][relevant_cols]

    mcps = len(curr_ctr_pubs[curr_ctr_pubs.drop(columns=['pmid', col_name]).any(axis=1)]['pmid'].unique())
    fig5_data.at[ctr, 'multiple_country_publications'] = mcps
    fig5_data.at[ctr, 'single_country_publications'] = len(curr_ctr_pubs['pmid'].unique()) - mcps

fig5_data["total_pubs"] = fig5_data["single_country_publications"] + fig5_data["multiple_country_publications"]
fig5_data = fig5_data.sort_values(by="total_pubs",)

fig5 = go.Figure(
    [
    go.Bar(name="Multiple Country Publications",
           x=fig5_data["multiple_country_publications"],
           y=[countries.capitalize_name(i) for i in fig5_data.index.tolist()],
           orientation="h"),
    go.Bar(name="Single Country Publications",
           x=fig5_data["single_country_publications"],
           y=[countries.capitalize_name(i) for i in fig5_data.index.tolist()],
           orientation="h"),
    ]
)
fig5.update_layout(
    barmode="stack",
    yaxis={"range": [len(fig5_data)-ctrs_to_show-0.5, len(fig5_data)-0.5],}
)
if show_plots:
    fig5.show()


# MeSH terms over time
terms_to_plot = 15
cumulative = True

# Find most to least common MeSH terms
unique_pmid_df = df.drop_duplicates(subset="pmid", keep="first")[["pmid", "pub_year", "mesh_terms"]].copy()

mesh_dict = {}
for i_mesh_terms in unique_pmid_df["mesh_terms"].tolist():
    for i_term in i_mesh_terms:
        if i_term not in mesh_dict:
            mesh_dict[i_term] = 1
        else:
            mesh_dict[i_term] += 1

mesh_sorted = sorted(mesh_dict.items(), key=lambda item: item[1], reverse=True)

year_range = [*range(int(df["pub_year"].min()), int(df["pub_year"].max()))]

fig6 = go.Figure()

term_by_year = []
for y in year_range:
    if cumulative:
        term_by_year.append(
            len(unique_pmid_df[unique_pmid_df["pub_year"] <= y])
        )
    else:
        term_by_year.append(
            len(unique_pmid_df[unique_pmid_df["pub_year"] == y])
        )
fig6.add_trace(
        go.Scatter(
            name="All Publications",
            x=year_range,
            y=term_by_year,
            visible="legendonly",
        )
)

for term, _ in mesh_sorted[:terms_to_plot]:
    i_df = unique_pmid_df.copy()
    i_df["has_mt"] = i_df["mesh_terms"].apply(lambda mts: term in mts)
    i_df = i_df[i_df["has_mt"]]

    term_by_year = []
    for y in year_range:
        if cumulative:
            term_by_year.append(
                len(i_df[i_df["pub_year"] <= y])
            )
        else:
            term_by_year.append(
                len(i_df[i_df["pub_year"] == y])
            )

    fig6.add_trace(
        go.Scatter(
            name=term,
            x=year_range,
            y=term_by_year,
            visible="legendonly" if term in ["Humans", "Female", "Pregnancy", "Adult", "Infant, Newborn"] else None
        )
    )
fig6.update_layout(
    yaxis={"title_text": "Total Publications" if cumulative else "Publications",},
    xaxis={"title_text": "Year", "range": [1960, 2024],}
)

if show_plots:
    fig6.show()


# Write all files with information file
figs_to_save = {"fig1": fig1,
                "fig2": fig2,
                "fig3": fig3,
                "fig4": fig4,
                "fig5": fig5,
                "fig6": fig6
                }

fh = PlotlyFigFileHandler()
for name, i_fig in figs_to_save.items():
    fh.add_fig(i_fig, name)

fh.save_all_figs_file(os.path.join("output", "all_fig_info.json"))