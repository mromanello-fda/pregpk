import os
import warnings
import pickle
import pandas as pd
from . import stdize_utils
from pregpk import gen_utils


def load_file_to_pandas(filepath):
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath, header=1)

    elif filepath.endswith('.csv'):
        # df = pd.read_csv(filepath, header=1)
        raise ValueError(".csv file path for input file not working anymore.")

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


def save_pkdb_as_split_pkl_strings(df, save_directory, max_filesize_bytes):
    estimated_size_bytes = len(pickle.dumps(df))

    n_splits = estimated_size_bytes // max_filesize_bytes + 1
    split_idxs = gen_utils.split_list(df.index.to_list(), len(df) // n_splits)

    for i, idxs in enumerate(split_idxs):
        with open(os.path.join(save_directory, f"pkdb_{i}.txt"), "wb") as i_pkl:
            i_pkl.write(pickle.dumps(df.iloc[idxs]))

    return
