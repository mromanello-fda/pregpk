import numpy as np


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


def get_param_plot_args(df, x_axis, group_by):
    # Reminder: this df is already filtered for only rows with the most common dimensionality

    params = ["auc", "c_min", "c_max", "t_half", "t_max", "cl"]
    cols = (f"{i}_stdized_val" for i in params)

    x_axis_to_col_name = {
        "dose": "dose_stdized_val",
        "gestational_age": "gestational_age_stdized_val"
    }

    # Plot args: needs x, y, name, legend/legendgroup?

    # Let's assume for now very simple; only parameters on y, x=0. But handle np.nans.

    plot_args = []
    # group_args = get_group_args(df, group_by, n_groups=5)

    if not group_by:
        group_args = [{"df_idxs": df.index.tolist(),
                       "group_name": "",
                       }]

    if group_by == "dose":
        group_args = []
        idxs, bounds = get_group_idxs_and_bounds_by_pctile(df, col="dose_stdized_val", n_groups=5)
        for i_idx, i_bound in zip(idxs, bounds):
            group_args.append({"df_idxs": i_idx,
                               "group_name": f"Dose: {i_bound[0]:.4g} - {i_bound[1]}"})

    if group_by == "gestational_age":
        group_args = []
        idxs, bounds = get_group_idxs_and_bounds_by_trimester(df)

    for igroup in group_args:
        i_group_df = df.loc[igroup["df_idxs"]]
        i_lg = igroup["group_name"]

        for col in cols:
            idf = i_group_df.dropna(axis=0, subset=[col])
            iy = idf[col].tolist()

            if x_axis in x_axis_to_col_name:
                ix = idf[x_axis_to_col_name[x_axis]]
            else:
                ix = [0]*len(iy)

            plot_args.append(
                {"x": ix, "y": iy, "legendgroup": i_lg}
            )

    return plot_args


def get_group_args(df, group_by, n_groups=5):

    if not group_by:
        return [{"df_idxs": df.index.tolist(),
                 "group_name": "",
                 }]

    group_idxs, group_bounds = get_group_idxs_and_bounds(df, group_by, n_groups)

    return group_args


def get_group_idxs_and_bounds(df, group_by, n_groups=5):

    # TODO: List of ways that you would group data by that would not simply be by percentiles
    if group_by == "gestational_age":
        pass

    if group_by == "dose":
        col_name = "dose_stdized_val"
        return get_group_idxs_and_bounds_by_pctile(df, col_name, n_groups)

    return


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
