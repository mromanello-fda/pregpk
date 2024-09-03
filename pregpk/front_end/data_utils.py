import pandas


def filter_df(df, filter_dict):

    if filter_dict["study_type"]:
        df = df[df['study_type'].isin(filter_dict["study_type"])]
    if filter_dict["drug"]:
        df = df[df['drug'].isin(filter_dict["drug"])]
    if filter_dict["disease_condition"]:
        df = df[df['disease_condition'].isin(filter_dict["disease_condition"])]

    df = df[(df["gestational_age_vr"] >= filter_dict["gest_age_range"][0]) & (df["gestational_age_vr"] <= filter_dict["gest_age_range"][1])]

    return df

