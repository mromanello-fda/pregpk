import os
import pandas as pd


def load_pkdb_from_local_csv(csv_path:str) -> pd.DataFrame:

    df = pd.read_csv(csv_path, header=0, dtype={'pmid':str})
    df['pmid'] = df['pmid'].fillna(value='')

    return df

