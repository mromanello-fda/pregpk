def filter_df(df, filter_dict):

    if filter_dict["study_type"]:
        df = df[df['study_type'].isin(filter_dict["study_type"])]
    if filter_dict["drug"]:
        df = df[df['drug'].isin(filter_dict["drug"])]
    if filter_dict["disease_condition"]:
        df = df[df['disease_condition'].isin(filter_dict["disease_condition"])]
    if filter_dict["route"]:
        df = df[df['route'].isin(filter_dict["route"])]

    if filter_dict["gest_age_range"] != [-10, 60]:  # TODO: Shouldn't hard code this?
        df = df[(df["gestational_age_vr"] >= filter_dict["gest_age_range"][0]) & (df["gestational_age_vr"] <= filter_dict["gest_age_range"][1])]
    if filter_dict["pub_year_range"] != [df["pub_year"].min(), df["pub_year"].max()]:  # TODO: Shouldn't hard code this?
        df = df[(df["pub_year"] >= filter_dict["pub_year_range"][0]) & (df["pub_year"] <= filter_dict["pub_year_range"][1])]

    return df


def sort_df(df, sort_dict):

    if sort_dict:
        sort_col = sort_dict[0]['column_id']

        # If sorting by params, must have the ability to sort different dimensionalities
        params = ["auc", "c_min", "c_max", "t_half", "t_max", "cl"]
        vr_cols = ["dose", "gestational_age"]

        if sort_col in params or sort_col in ["dose"]:
            df["dim_freq"] = df[f"{sort_col}_dim"].map(df[f"{sort_col}_dim"].value_counts())

            df = df.sort_values(
                by=[f'dim_freq', f'{sort_col}_stdized_val'],
                ascending=[False, sort_dict[0]['direction'] == "asc"],
                axis=0
            )

        elif sort_col in ["gestational_age"]:
            df = df.sort_values(
                by=[f'{sort_col}_stdized_val'],
                ascending=[sort_dict[0]['direction'] == "asc"],
                axis=0
            )

        else:
            df = df.sort_values(
                by=sort_col,
                ascending=sort_dict[0]['direction'] == "asc",
                axis=0
            )

    return df



