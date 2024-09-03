from typing import Any
import warnings
import pandas as pd


def add_dict_to_df_using_reference_column(df: pd.DataFrame, data: dict, ref_col: Any, new_col: Any, default: Any=None,
                                          override_existing: bool=False) -> pd.DataFrame:
    """
    Adds data from a dictionary to a current DataFrame, where the row in which the data is added is chosen by
    referencing an existing column in the DataFrame (which should contain unique values).
    :param df: pandas.DataFrame with current data
    :param data: dictionary containing data to be added to df
    :param ref_col: name column of df whose values will be used to define where data will be added
    :param new_col: name of new column where data will be added
    :param default: Any, default value of data if value in ref_col is not found in data.keys()
    :param override_existing: bool, whether value in new_col should be overwritten if it currently exists
    :return: pandas.DataFrame with new_col.
    """
    if new_col in df.columns:
        if not override_existing:
            warnings.warn(f'DataFrame already contained column {new_col}. If you want to override current values,'
                          f'set override_existing to True.')
            return df

    ref_vals = set(df[ref_col].tolist())
    new_vals = data.keys()
    n_shared_vals = len(set(ref_vals) & set(new_vals))
    if len(ref_vals) > n_shared_vals:
        warnings.warn(f"{len(ref_vals) - n_shared_vals} rows of column {ref_col} do not have counterparts as keys in "
                      f"updating dictionary, and thus will not be updated")
    if len(new_vals) > n_shared_vals:
        warnings.warn(f"{len(new_vals) - n_shared_vals} keys in updating dictionary dont have matches in {ref_col} of "
                      f"DataFrame, and thus won't be added.")

    for idx, row in df.iterrows():
        ref_val = row[ref_col]
        if ref_val in data:
            df.at[idx, new_col] = data[ref_val]
        else:
            df.at[idx, new_col] = default

    return df


def filter_dataset_for_testing(text_df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes rows of data that don't meet requirements to be used in automated publication selection testing.
    """
    not_reviewed = text_df.index[~text_df['been_reviewed']].tolist()  # Articles not reviewed by Emily
    is_review_art = text_df.index[text_df['is_review']].tolist()  # Review articles
    not_english = text_df.index[~text_df['is_english']].tolist()  # Non-english articles
    remove = list(set(not_reviewed + is_review_art + not_english))

    print(f'Removing:\n'
          f'\t{len(not_reviewed)} publications as they have not been reviewed by Emily\n'
          f'\t{len(is_review_art)} publications as they are review articles\n'
          f'\t{len(not_english)} publications as they are not in English\n'
          f'\t{len(remove)} publications in total\n')

    text_df = text_df.drop(remove, axis=0)

    return text_df


def dataset_from_text_df(text_df: pd.DataFrame, sections) -> dict:
    # TODO: this is terrible. assumes everything from pubtator.
    sections_to_include = ["title", "abstract", "intro", "methods", "results", "fig", "table", "discuss", "concl", "abbr"]

    dataset = {}
    for idx, row in text_df.iterrows():
        dataset[idx] = {}

        # Text
        if 'title' in sections:
            dataset[idx]['title'] = row['title']
        if 'abstract' in sections:
            dataset[idx]['abstract'] = row['title']
        if 'fulltext' in sections:
            for sec in sections_to_include:
                if sec in row['pubtator_text']:
                        dataset[idx][sec] = row['pubtator_text'][sec]

        # Has PK data
        dataset[idx]['has_pk_data'] = row['has_pk_data']

    return dataset


def merge_pubmed_api_text_dfs(edf, pdf, conflict_priority='both', conflict_dict=None,
                              article_join='outer'):

    # Create full conflict_priority_dict
    conflict_set = set(edf.columns) & set(pdf.columns)
    if conflict_dict is None:
        conflict_dict = {}
    for conflict in conflict_set:
        if conflict not in conflict_dict:
            conflict_dict[conflict] = conflict_priority

    # Drop opposing priority
    edf = edf.drop(labels=[col for col, priority in conflict_dict.items() if priority == 'pubtator'], axis=1)
    pdf = pdf.drop(labels=[col for col, priority in conflict_dict.items() if priority == 'entrez'], axis=1)

    # Rename columns for "both" priority
    edf = edf.rename(mapper={col: 'entrez_'+col for col, priority in conflict_dict.items() if priority == 'both'}, axis=1)
    pdf = pdf.rename(mapper={col: 'pubtator_'+col for col, priority in conflict_dict.items() if priority == 'both'}, axis=1)

    df = pd.concat([edf, pdf], axis=1, join=article_join)
    removed_articles = set(edf.index.tolist() + pdf.index.tolist()) - set(df.index)
    if removed_articles:
        print("\nFollowing PMIDs were removed when merging Entrez and Pubmed APIs due to\n"
              "one of the APIs not returning any data for them (to prevent, use 'article_join=outer'): ")
        for i in removed_articles:
            print(f"\t- {i}")

    return df
