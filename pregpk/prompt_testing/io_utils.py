import os
import re
import tkinter as tk
from tkinter import filedialog

# TODO: This is relevant beyond just testing prompts, but it will remain here for the time being


def input_pmids():
    user_in = input(f'Input:\n'
                    f'\t- "pmid" if you want to write or use a file with specific PMIDs\n'
                    f'\t- "query" if you want to write or use a file with a PubMed query\n')

    if user_in == "pmid":
        print('')
        pmids = input_raw_pmids()

    elif user_in == "query":
        print('')
        query = input_query()

    return pmids


def input_raw_pmids():

    user_in = input(f'Input:\n'
                    f'\t- A list of PMIDs separated by commas/spaces, or\n'
                    f'\t- "file", if selecting a .txt/.csv file with a list of PMIDs or\n')



    if user_in == "file":
        tk.Tk().withdraw()
        pmids_filename = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="PMID list",
                                      filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv")))

        with open(pmids_filename, 'r') as pmids_file:
            user_input = pmids_file.read()
    else:
        user_input = user_in.replace(' ', ',')

    split_input = [i for i in re.split(r"[\s,]+", user_input) if i]  # Remove empty strings
    pmids = list(dict.fromkeys([i for i in split_input if i.isdigit()]))  # Must be number
    if set(split_input) - set(pmids):
        print("\nSome inputted PMIDs deleted because of invalid format:")
        for i in set(split_input) - set(pmids):
            print(f"\t- {i}")

    # Remove leading zeros
    corr_pmids = [i.lstrip('0') for i in pmids]
    if set(corr_pmids) - set(pmids):
        print("\nRemoving leading zeros from following PMIDs:")
        for i in set(pmids) - set(corr_pmids):
            print(f"\t- {i} -> {i.lstrip('0')}")

    return corr_pmids


def input_query():

    user_in = input(f'Please input:\n'
                    f'\t- A query, or\n'
                    f'\t- "file", if selecting a .txt/.csv file with a list of PMIDs or\n')

    if user_in == "file":
        tk.Tk().withdraw()
        query_filename = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Query",
                                      filetypes=(("Text Files", "*.txt"),))

        with open(query_filename, 'r') as pmids_file:
            query = pmids_file.read()
    else:
        query = user_in

    return query



