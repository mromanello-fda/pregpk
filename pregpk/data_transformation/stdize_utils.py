import os
import warnings
import re
import json
from types import MappingProxyType
import numpy as np
import pandas as pd
import pycountry
from pregpk import gen_utils
from pregpk.ValueRange import ValueRange, GestAgeValueRange


def convert_to_ValueRange(ele):
    """
    Converts string to a ValueRange object or return nan; useful for mapping a full pandas DataFrame column with
    strings to a column with sortable ValueRanges
    :param ele:
    :return:
    """
    try:
        return ValueRange(ele)
    except (ValueError, TypeError):
        return np.nan

    # TODO: This should not be necessary (AssertionError)
    except AssertionError:
        return np.nan


def check_ValueRange_for_expected_dimensions(vr, expected_dims, invalid_return=np.nan):

    if isinstance(vr, ValueRange):

        if not vr.unit:  # If never assigned, vr.unit is still None
            if "" in expected_dims:  # dimensionless allowed?
                return vr
            else:
                return invalid_return

        else:  # if has a pint unit
            dims = vr.unit.dimensionality

            if not dims:  # has a pint unit but is assigned dimensionless unit (not expected)
                if "" in expected_dims:
                    return vr

            else:
                for i_dim in dict(dims):  # {dimension: power}
                    if i_dim not in expected_dims:
                        return invalid_return
                return vr  # If full for loop runs and nothing outside of expected_dims

    else:
        raise TypeError("Input must be a ValueRange object.")


def check_ValueRange_for_expected_dimensionality(vr, expected_dims, invalid_return=np.nan):

    if isinstance(vr, ValueRange):

        if not vr.unit:  # If never assigned, vr.unit is still None
            if "" in expected_dims:  # dimensionless allowed?
                return vr
            else:
                return np.nan

        else:  # if has a pint unit
            dims = vr.unit.dimensionality

            if not dims:  # has a pint unit but is assigned dimensionless unit (not expected)
                if "" in expected_dims:
                    return vr

            else:
                for i_dim in dict(dims):  # {dimension: power}
                    if i_dim not in expected_dims:
                        return invalid_return
                return vr  # If full for loop runs and nothing outside of expected_dims

    else:
        raise TypeError("Input must be a ValueRange object.")


def convert_to_GestAgeValueRange(ele):
    """
    Converts string to a ValueRange object or return nan; useful for mapping a full pandas DataFrame column with
    strings to a column with sortable ValueRanges
    :param ele:
    :return:
    """
    try:
        return GestAgeValueRange(ele)
    except (ValueError, TypeError):
        return np.nan


def country_from_affiliation(aff):
    us_state_dict = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts',
        'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
        'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
        'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
        'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
        'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    countries = [i.name.lower() for i in pycountry.countries]
    re_any_country = "|".join(countries)
    re_any_state = "|".join(us_state_dict.values())
    re_any_state_init = "|".join(us_state_dict.keys())

    matches = re.findall(re_any_country, aff.lower())  # TODO: Finish this? not even sure what i was doing
    if matches:
        matches



    return


def replace_strange_characters(val):
    if isinstance(val, str):
        val = val.replace('\u2013', '\u002d').\
            replace('\u202c', '').\
            replace('\u202f', ' ').\
            replace('\xa0', ' ').\
            replace('\u2009', ' ').\
            replace('\u2007', ' ').\
            replace('\u03BC', '\u00B5')
        return val
    if isinstance(val, list):
        return [replace_strange_characters(i) for i in val]
    return val


def replace_strange_characters_from_df(df):
    df = df.map(replace_strange_characters)
    return df


def standardize_column_names(df):
    column_name_mapper = {'Study (Pubmed ID)': 'pmid',
                          'Reference': 'reference',
                          'Study Type': 'study_type',
                          'N (number of subjects)': 'n',
                          'Maternal/Fetal': 'maternal_or_fetal',
                          'Gestational Age (weeks)': 'gestational_age',
                          'Trimester 0 (Y/N)': 'tri_0',
                          'Trimester I (Y/N)': 'tri_1',
                          'Trimester II (Y/N)': 'tri_2',
                          'Trimester III (Y/N)': 'tri_3',
                          'Other (Y/N)': 'tri_other',
                          'Maternal Age (years)': 'maternal_age',
                          'Maternal Weight (units)': 'maternal_weight',
                          'Maternal BMI': 'maternal_bmi',
                          'Disease Condition Indicated': 'disease_condition',
                          'Ethnicity': 'ethnicity',
                          'Drug': 'drug',
                          'Dose (units)': 'dose',
                          'Frequency of Dosing ': 'dosing_frequency',
                          'Route': 'route',
                          'Cmax (units)': 'c_max',
                          'AUC (units)': 'auc',
                          'Tmax (units)': 't_max',
                          'T1/2 (units)': 't_half',
                          'CL (units)': 'cl',
                          'Cmin (units)': 'c_min',
                          'Other Maternal PK Data (Units)': 'other_pk_data',
                          'Time after dose': 'time_after_dose',
                          'Doses taken previously': 'doses_taken_previously',
                          'Fetal PK Data': 'fetal_pk_data',
                          'When Fetal PK Data was taken': 'when_fetal_data_was_taken',
                          'Maternal Fetal Ratio': 'maternal_fetal_ratio',
                          'Infant PK Data': 'infant_pk_data',
                          'Plasma Conc-Time curve? (Y/N) ': 'has_plasma_conc_time_curve',
                          'Notes': 'notes',
                          'GSRS UNII': 'gsrs_unii',
                          'ATC Code': 'atc_code',
                          'Language': 'language',
                          'Unnamed: 35': 'notes_2',
                          'Unnamed: 37': 'notes_3',
                          }

    missing_columns = set(df.columns) - set(column_name_mapper.keys())
    if missing_columns:
        raise ValueError(f'Unexpected name(s) {", ".join(list(missing_columns))} in input DataFrame. '
                         f'Must edit mapper dictionary in "stdize_utils.standardize_column_names"'
                         f' to include all possible column names.')
    df = df.rename(mapper=column_name_mapper, axis=1, )

    return df


def standardize_column_dtypes(df):

    # TODO: There is a way to do this with the native read_csv or read_excel function that you should use instead
    df['pmid'] = df['pmid'].astype(str)
    df['gestational_age'] = df['gestational_age'].astype(str)
    df['maternal_age'] = df['maternal_age'].astype(str)
    df['drug'] = df['drug'].astype(str)
    df['dose'] = df['dose'].astype(str)
    df['c_max'] = df['c_max'].astype(str)
    df['auc'] = df['auc'].astype(str)
    df['t_max'] = df['t_max'].astype(str)
    df['t_half'] = df['t_half'].astype(str)
    df['cl'] = df['cl'].astype(str)
    df['c_min'] = df['c_min'].astype(str)
    df['gsrs_unii'] = df['gsrs_unii'].astype(str)

    return df


def standardize_values(df, standard_values_directory):
    # TODO: There is a way to do this with the native read_csv or read_excel function that you should use instead
    df['pmid'] = df['pmid'].apply(lambda raw_pmid: standardize_pmid(raw_pmid)).astype(str)
    df['pmid_hyperlink'] = df['pmid'].apply(lambda pmid: f'[{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid})')
    df = df.apply(lambda row: standardize_study_type(row, standard_values_directory), axis=1)
    df['n'] = df['n'].apply(lambda raw_n: standardize_n(raw_n))
    df = df.apply(lambda row: standardize_maternal_or_fetal_data(row), axis=1)
    # df = df.apply(lambda row: standardize_trimesters(row), axis=1)
    df['drug'] = df['drug'].str.strip()

    df['drug_hyperlink'] = df.apply(lambda row: f"[{row['drug']}](https://gsrs.ncats.nih.gov/ginas/app/ui/substances/{row['gsrs_unii']})", axis=1)

    dose_dimensions = ["[time]", "[mass]", "[length]", "[substance]", ""]  # Include dimensionless
    df = df.apply(lambda row: standardize_dose(row, dose_dimensions), axis=1)
    df = df.apply(lambda row: standardize_gestational_age(row), axis=1)

    # Handle parameters
    params = ['c_max', 'auc', 't_max', 't_half', 'cl', 'c_min']
    param_dimensions = ["[time]", "[mass]", "[length]", "[volume]",
                        "[substance]", "[international_unit]", "[equivalent]", ""]
    df = df.apply(lambda row: standardize_parameters(row, params, param_dimensions), axis=1)

    df["other_pk_data_vr"] = df["other_pk_data"].apply(convert_to_ValueRange).apply(
        lambda x: check_ValueRange_for_expected_dimensions(x, param_dimensions) if isinstance(x, ValueRange)
        else np.nan
    )

    df["time_after_dose_vr"] = df["time_after_dose"].apply(convert_to_ValueRange).apply(
        lambda x: check_ValueRange_for_expected_dimensions(x, ["[time]"]) if isinstance(x, ValueRange)
        else np.nan
    )

    return df


def standardize_pmid(raw_pmid):
    # Rules: PMID must be digit and can't be nan

    if re.fullmatch(r"\d+", raw_pmid):
        return raw_pmid

    if isinstance(raw_pmid, str):  # If has an inadvertent space or character
        pmid = re.sub(r"\D", "", raw_pmid)  # Remove digits; assumes the rest is correct
        warnings.warn(f'PMID "{raw_pmid}" contains unexpected non-numeric character (letter, space, etc.). '
                      f'Changing to "{pmid}".')
        return pmid

    if isinstance(raw_pmid, float):  # Probably nan (or has period and is now a float with decimal)
        if np.isnan(raw_pmid):
            return ''  # Empty PMID; return empty string

    warnings.warn(f"PMID {raw_pmid} not interpretable. Please fix in imported file.")  # Unable to read
    return ''


def standardize_study_type(row, standard_values_directory):

    known_sts = gen_utils.load_csv_to_list(os.path.join(standard_values_directory, 'study_types.csv'))
    sts_to_col_name = {i: f'is_{re.sub("[ -]", "_", i)}_study'.lower() for i in known_sts}

    # Add new columns for OHE (indexes here because row is a series)
    row = pd.concat(
        [row,
         pd.Series({i: False for i in sts_to_col_name.values()}, dtype=bool)
         ]
    )

    # Split into list of study types divided by " and " or comma
    raw_study_type = row['study_type'].lower().replace(' study', '')
    splits = [' and ', ',']
    study_types = [i for i in split_by_substrings(raw_study_type, splits) if i]  # Split by substrings, remove empty strings

    # Specific cases
    for i, st in enumerate(study_types):
        if st == 'cross-over':  # Standardize grammar
            study_types[i] = 'crossover'
        if st == 'pilot study':  # "Study" redundant
            study_types[i] = 'pilot'

    # Check if all are within known study types
    for i, st in enumerate(study_types):
        if st not in known_sts:
            warnings.warn(f'Study type "{st}" not a known study type. Removing from study_type list. If correct, '
                          f'add to {standard_values_directory}/study_types.csv file.')
            study_types.pop(i)

    for st in study_types:
        row[sts_to_col_name[st]] = True

    return row


def split_by_substrings(text, substrings):
    # By ChatGPT

    # Join the substrings with a pipe '|' to create the regex pattern
    pattern = '|'.join(map(re.escape, substrings))
    # Use re.split() to split the string x by the pattern
    return re.split(pattern, text)


def standardize_n(raw_n):
    # Will convert to float instead of int because the inclusion of np.nans in a column (propagated from empty cells or
    #  "N/A" in spreadsheet) requires that column to be float type.
    # TODO: What is N/A on spreadsheet? Does that mean it's not reported?

    if isinstance(raw_n, float):  # Includes nans
        return raw_n

    if isinstance(raw_n, int):  # Likely
        return float(raw_n)

    if isinstance(raw_n, str):  # Might just be mistake/error reading, might be range

        if raw_n.isdigit():  # If just a string with a number, eg. "4"
            return int(raw_n)

        if '-' in raw_n:  # TODO: range; I have no clue how to deal with this
            warnings.warn(
                "Range detected for n / subject number in a study. For now, the minimum value will be selected.")
            try:
                n_range = [int(raw_n[:raw_n.index('-')]), int(raw_n[raw_n.index('-') + 1:])]
                return min(n_range)
            except ValueError:
                warnings.warn("Range detected for n / subject number but was unable to parse to minimum and maximum. "
                              "N will be set to np.nan")
                return np.nan

    warnings.warn(f"Value {raw_n} for n / number of subjects not interpretable. Please fix in imported file.")
    return np.nan


def standardize_maternal_or_fetal_data(row):
    row.loc['has_maternal_data'] = False
    row.loc['has_fetal_data'] = False

    # if row['maternal_or_fetal'].lower() not in ['maternal', 'fetal', 'both']:
    #     raise ValueError(f"Row {row.name}: Unable to interpret maternal/fetal value. Must be 'Maternal', "
    #                      f"'Fetal', or 'Both' ")

    if row['maternal_or_fetal'].lower() in ['maternal', 'both']:
        row['has_maternal_data'] = True

    if row['maternal_or_fetal'].lower() in ['fetal', 'both']:
        row['has_fetal_data'] = True

    return row


def standardize_gestational_age(row):

    gvr = convert_to_GestAgeValueRange(row["gestational_age"])
    row = pd.concat([row,
                     pd.Series(index=["gestational_age_vr", "gestational_age_stdized_val", "has_non_pregnant",
                                      "has_tri_1", "has_tri_2", "has_tri_3", "has_delivery", "has_postpartum"])])

    if isinstance(gvr, GestAgeValueRange):
        stdized_val = float(gvr)
        row.loc[["has_non_pregnant", "has_tri_1", "has_tri_2", "has_tri_3", "has_delivery", "has_postpartum"]] = [
            gvr.has_non_pregnant, gvr.has_tri_1, gvr.has_tri_2, gvr.has_tri_3, gvr.has_delivery, gvr.has_postpartum
        ]

    else:
        stdized_val = np.nan
        row.loc[["has_non_pregnant", "has_tri_1", "has_tri_2", "has_tri_3", "has_delivery", "has_postpartum"]] = False

    row["gestational_age_vr"] = gvr
    row["gestational_age_stdized_val"] = stdized_val

    return row


# TODO: maybe standardize the three functions below into a single function
def standardize_dose(row, dose_dimensions):

    vr = convert_to_ValueRange(row["dose"])

    if isinstance(vr, ValueRange):
        vr = check_ValueRange_for_expected_dimensions(vr, dose_dimensions)

    if pd.isna(vr):
        dim = np.nan
        stdized_val = np.nan

    else:
        if vr.unit is None:
            dim = None
            stdized_val = np.nan

        else:
            dim = vr.unit.dimensionality
            stdized_val = float(vr) * (1 * vr.unit).to_base_units().magnitude

    row.at[f"dose_vr"] = vr
    row.at[f"dose_dim"] = dim
    row.at[f"dose_stdized_val"] = stdized_val

    return row


def standardize_parameters(row, params, param_dimensions):

    for param in params:

        vr = convert_to_ValueRange(row[param])
        if isinstance(vr, ValueRange):
            vr = check_ValueRange_for_expected_dimensions(vr, param_dimensions)

        if pd.isna(vr):  # Unable to convert
            dim = np.nan
            stdized_val = np.nan

        else:
            if vr.unit is None:
                dim = None
                stdized_val = vr.sort_val
            else:
                dim = vr.unit.dimensionality
                stdized_val = float(vr) * (1 * vr.unit).to_base_units().magnitude

        row.at[f"{param}_vr"] = vr
        row.at[f"{param}_dim"] = dim
        row.at[f"{param}_stdized_val"] = stdized_val

    return row


def convert_yn_to_bool(val):
    if val.lower() == 'y':
        return True
    if val.lower() == 'n':
        return False

    raise ValueError(f"Unable to convert value {val} to boolean, since either y/Y/n/N are assumed.")


def get_drug_dropdown_json_from_gsrs(df, json_save_path,
                                     null_gsrs_vals=("", "non-approved record", "nan")):

    # TODO: Deal with values without UNIIs
    grouped = df.groupby('gsrs_unii')['drug'].apply(lambda x: x.value_counts().index.tolist())

    # Create the dictionary mapping by joining names in each list by slashes
    # By ChatGPT
    drug_to_unii = {"/".join(drugs): unii for unii, drugs in sorted(grouped.items())}
    drug_to_unii = dict(sorted(drug_to_unii.items(), key=lambda item: item[0].lower()))

    with open(json_save_path, 'w') as json_file:
        json.dump(drug_to_unii, json_file, indent=4)

    return


