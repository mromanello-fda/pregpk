import warnings
import pandas as pd

def load_file_to_pandas(filepath):

    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath, header=1)

    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath, header=1)

    else:
        raise ValueError("File path with PK database must be either .csv or .xlsx file")

    # Check if we have the data types we expect
    types_df = df.map(type)  # df with all datatypes
    unique_types = pd.unique(types_df.values.ravel())
    for t in unique_types:
        if t not in [int, str, float]:
            warnings.warn("File loaded correctly but contains unexpected datatypes; check for validity.")

    df = stdize_utils.replace_strange_characters_from_df(df)

    return df
