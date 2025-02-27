import numpy as np
import plotly.colors as pcolors


def row_and_col_subplot_positions(n_rows, n_cols, direction="horizontal"):

    if direction == "horizontal":
        rows = [i for i in range(1, n_rows+1) for _ in range(1, n_cols+1)]
        cols = [*range(1, n_cols+1)]*n_rows

    elif direction == "vertical":
        rows = [*range(1, n_rows+1)]*n_cols
        cols = [i for i in range(1, n_cols+1) for _ in range(1, n_rows+1)]

    else:
        raise ValueError("direction must be either 'horizontal' (default) or 'vertical'.")

    return rows, cols


def get_param_plot_group_args(df, x_axis, group_by, n_groups):
    # TODO: need to document this better; variable names are not descriptive at all.
    # Reminder: this df is already filtered for only rows with the most common dimensionality

    params = ["auc", "c_min", "c_max", "t_half", "t_max", "cl"]
    cols = tuple(f"{i}_stdized_val" for i in params)

    x_axis_to_col_name = {
        "dose": "dose_stdized_val",
        "gestational_age": "gestational_age_stdized_val"
    }

    if not group_by:
        group_args = [{"df_idxs": df.index.tolist(),
                       "group_name": "",
                       "color": "rgba(0, 0, 256, 0.5)"
                       }]

    elif group_by == "dose":
        group_args = []
        idxs, bounds = get_group_idxs_and_bounds_by_pctile(df, col="dose_stdized_val", n_groups=5)
        colors = interpolate_colors([0, 0, 256, 0.5], [256, 0, 0, 0.5], n_groups)
        for i_idx, i_bound, color in zip(idxs, bounds, colors):
            group_args.append({"df_idxs": i_idx,
                               # TODO: unit and number of sig figs hard coded; should dynamically update
                               "group_name": f"Dose: {i_bound[0]:.4g} - {i_bound[1]:.4g} mg",
                               "color": color,
                               })

    elif group_by == "gestational_age":
        group_args = []
        idxs, bounds = get_group_idxs_and_bounds_by_trimester(df)
        colors = interpolate_colors([0, 0, 256, 0.5], [256, 0, 0, 0.5], n=6)
        for i_idx, i_bound, color in zip(idxs, bounds, colors):
            group_args.append({"df_idxs": i_idx,
                               "group_name": f"{i_bound}",
                               "color": color,
                               })

    plot_group_args = []
    for ig, i_group_args in enumerate(group_args):
        i_group_df = df.loc[i_group_args["df_idxs"]]
        i_lg = i_group_args["group_name"]
        color = i_group_args["color"]

        group = []

        for col in cols:
            # idf = i_group_df.dropna(axis=0, subset=[col])  # TODO: might be unnecessary now that filtering is done before. Might help speed by reducing number of points to plot though?
            iy = i_group_df[col].tolist()

            if x_axis in x_axis_to_col_name:
                ix = i_group_df[x_axis_to_col_name[x_axis]]
            else:
                ix = [0]*len(iy)

            group.append(
                {"x": ix, "y": iy, "legendgroup": i_lg, "color": color}
            )

        plot_group_args.append(group)

    return plot_group_args


def get_group_idxs_and_bounds_by_pctile(df, col, n_groups):

    pctiles = np.linspace(0, 100, n_groups+1)
    pctile_values = np.nanpercentile(df[col], pctiles)

    bounds = [[pctile_values[i], pctile_values[i + 1]] for i in range(n_groups)]
    idxs = []
    for [min_bound, max_bound] in bounds:
        idxs.append(
            df[(df[col] >= min_bound) & (df[col] < max_bound)].index.tolist()
        )
    idxs[-1].extend(df[df[col] >= pctile_values[-1]].index.tolist())

    return idxs, bounds


def get_group_idxs_and_bounds_by_trimester(df, exclusive=False):

    cols = ["has_non_pregnant", "has_tri_1", "has_tri_2", "has_tri_3", "has_delivery", "has_postpartum"]
    tri_df = df[cols]

    bounds = ["Non-Pregnant", "1st Trimester", "2nd Trimester", "3rd Trimester", "Delivery", "Postpartum"]
    idxs = []
    for col in cols:
        if not exclusive:
            idxs.append(tri_df[tri_df[col]].index.tolist())
        if exclusive:  # Remove from every list of index any index that is found in other lists
            idxs.append(df[
                            (tri_df[col]) & (~tri_df.loc[:, df.columns != col].any(axis=1))
            ])

    return idxs, bounds


def interpolate_colors(c1, c2, n):
    # TODO: Add ValueErrors if c1, c2 have RBG values greater than [256, 256, 256, 1] or are not length 3 or 4
    #  (if 3, assume a=1)
    """
    Generates a list of colors that interpolate between color1 and color2.

    Parameters:
    - color1: Starting color in RGBA format (e.g., [1, 0, 0, 1]).
    - color2: Ending color in RGBA format (e.g., [0, 0, 1, 1]).
    - n: Number of colors to generate.
    - output: "rgba" for RGBA output or "hex" for hex color output.

    Returns:
    - List of colors in the specified format.
    """
    # Convert colors to numpy arrays
    c1 = np.array(c1)
    c2 = np.array(c2)

    # Interpolate each component (R, G, B, A) between color1 and color2
    interpolated_colors = np.array([
        (1 - i) * c1 + i * c2 for i in np.linspace(0, 1, n)
    ])

    return [f"rgba({color[0]:.0f}, {color[1]:.0f}, {color[2]:.0f}, {color[3]})" for color in interpolated_colors]
