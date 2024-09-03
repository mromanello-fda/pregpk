import os
import json
import time
from Bio import Entrez
from tqdm import tqdm
import pandas as pd
from pregpk import gen_utils
from pregpk.countries import CountryParser


def is_fill_invalid_option_allowed(fill_invalid_val):  # Must either be "remove" or falsey value
    return (fill_invalid_val == 'remove') or not fill_invalid_val


def text_from_pmids(pmids: list, email: str, api_key: str = None, fill_invalid_pmids="remove") -> dict:
    """
    Fetches all text available from Entrez API for a list of PMIDs. Returned text is split into sections (title,
    abstract, methods, etc.), although usually Entrez only returns article titles and abstracts.
    :param pmids: list of PMID strings to obtain texts from Entrez
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :return: nested dict where PMIDs (keys) map onto a dictionary containing sections of text returned from Entrez.
        eg. {'1234': {'title': 'Review of Current Literature', 'abstract':'We present a review of current literature.'},
             '0111': {'title': 'Effects of chemotherapy'}}
    """

    if not is_fill_invalid_option_allowed(fill_invalid_pmids):
        raise ValueError('fill_invalid_pmid must be either "remove" or a falsey value, like None or {}')

    print('\nLoading abstracts for all articles using Entrez API...')
    time.sleep(0.1)

    Entrez.email = email
    if api_key is not None:
        Entrez.api_key = api_key
    max_pmids_per_call = 9999

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    texts = {}

    for i_pmids in tqdm(split_pmids):
        i_handle = Entrez.efetch(db="pubmed", id=gen_utils.comma_sep_str_from_list(i_pmids),
                                 rettype="xml", retmode="text")
        i_responses = Entrez.read(i_handle)
        i_responses = gen_utils.convert_to_python_obj(i_responses)
        i_handle.close()

        for article in i_responses['PubmedArticle']:
            try:
                abstract = article['MedlineCitation']['Article']['Abstract']['AbstractText']
                abstract = " ".join(abstract)
                art_text = {'abstract': abstract}
            except KeyError:
                art_text = {}

            texts[article['MedlineCitation']['PMID']] = art_text

    invalid_pmids = set(pmids) - set(texts.keys())
    if invalid_pmids and fill_invalid_pmids != "remove":
        texts.update({i: fill_invalid_pmids for i in invalid_pmids})

    return texts


def pmids_from_pubmed_query(query: str, email: str, api_key: str = None, free_articles_only: bool = False) -> list:
    """
    Fetches all PMIDs returned by a PubMed search query.
    :param query: string with PubMed query
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :param free_articles_only: boolean, whether to return only PMIDs containing free full texts
    :return: list containing PMIDs returned by PubMed search of inputted query
    """

    print('\nGetting PMIDs returned by query through Entrez API...')

    Entrez.email = email
    if api_key is not None:
        Entrez.api_key = api_key

    if free_articles_only:
        query = query + ' AND "freetext"[filter]'
        # query = query + ' AND "free only pmc"[filter]'

    handle = Entrez.esearch(db='pubmed', term=query, retmax=10000, sort='pub_date', datetype='pdat')
    response = Entrez.read(handle)
    response = gen_utils.convert_to_python_obj(response)
    handle.close()

    total = int(response['Count'])
    pmids = response['IdList']  # Convert to python native list and string

    if total < 10000:
        return pmids

    while len(pmids) < total:
        last_date = Entrez.read(Entrez.esummary(db='pubmed', id=pmids[-1], retmode='text'))[0]['PubDate'][
                    :4]  # String with YYYY

        i_handle = Entrez.esearch(db='pubmed', term=query, retmax=10000, sort='pub_date', datetype='pdat',
                                  mindate=0000, maxdate=last_date)
        i_response = Entrez.read(i_handle)
        i_response = gen_utils.convert_to_python_obj(i_response)
        i_handle.close()

        i_pmids = i_response['IdList']
        pmids += i_pmids[i_pmids.index(pmids[-1]) + 1:]

    print(f"{total} PMIDs returned from PubMed query.")

    return pmids


def summaries_from_pmids(pmids: list, email: str, api_key: str = None, fill_invalid_pmids='remove') -> dict:
    # TODO: If you end up merging this module with the original entrez_utils, this function actually changed a fair bit
    #  in order to add author affiliation country and MeSH terms.
    """
    Returns Entrez esummaries for a list of PMIDs as a nested dict.
    :param pmids: list of PMIDs
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :return: nested dict with Entrez summaries for each of the queries PMIDs
        eg. {'1234': returned Entrez esummary json/dict,
             '0111': returned Entrez esummary json/dict}
    """
    Entrez.email = email
    if api_key is not None:
        Entrez.api_key = api_key
    max_pmids_per_call = 9999

    cp = CountryParser()

    if not is_fill_invalid_option_allowed(fill_invalid_pmids):
        raise ValueError('fill_invalid_pmid must be either "remove" or a falsey value, like None or {}')

    # Check whether PMIDs are valid for Entrez API
    pmids, invalid_pmids = remove_invalid_pmids(pmids=pmids, email=email, api_key=api_key,
                                                verbose=False, return_invalid=True)

    if invalid_pmids:
        print("The following inputted PMIDs are invalid and will not return summaries/metadata:")
        for i in invalid_pmids:
            print(f"\t- {i}")
        print('')

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)

    summaries = {}
    for i_pmids in split_pmids:
        i_handle = Entrez.esummary(db='pubmed', id=gen_utils.comma_sep_str_from_list(i_pmids), retmode='xml')
        i_resp = Entrez.read(i_handle)
        i_resp = gen_utils.convert_to_python_obj(i_resp)
        i_summaries = {i['Id']: i for i in i_resp}
        i_handle.close()

        i_handle = Entrez.efetch(db='pubmed', id=gen_utils.comma_sep_str_from_list(i_pmids), retmode='xml')
        i_resp = Entrez.read(i_handle)
        i_resp = gen_utils.convert_to_python_obj(i_resp)
        for art in i_resp['PubmedArticle']:
            art_pmid = art['MedlineCitation']['PMID']
            try:
                mesh_terms = [i['DescriptorName'] for i in art["MedlineCitation"]['MeshHeadingList']]
            except KeyError:
                mesh_terms = []

            aff_set = set()
            # Better to have two try-except statements because sometimes there are some authors with AffiliationInfo
            # and some without; using only one try-except statement would ignore the authors with data
            try:
                for auth in art["MedlineCitation"]["Article"]["AuthorList"]:
                    try:
                        aff_set.update([i['Affiliation'] for i in auth["AffiliationInfo"]])
                    except (KeyError, IndexError):
                        pass
            except KeyError:
                pass

            aff_ctrs = set()
            for aff in aff_set:
                aff_ctrs.update(cp.countries_from_affiliation(aff))
            aff_ctrs = list(set(aff_ctrs))

            i_summaries[art_pmid].update({"mesh_terms": mesh_terms, "pub_countries": aff_ctrs})

        summaries.update(i_summaries)

    if fill_invalid_pmids != 'remove':
        summaries.update({i: fill_invalid_pmids for i in invalid_pmids})  # Fill in invalid PMIDs

    return summaries


def metadata_from_pmids(pmids: list, email: str, api_key: str = None, fill_invalid_pmids='remove') -> dict:
    # TODO: If you end up merging this module with the original entrez_utils, this function actually changed a fair bit
    #  in order to add author affiliation country and MeSH terms.
    """
    :param pmids: list of PMIDs
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :return: nested dict with article metadata returned by Entrez API
        eg. {
            '1234': {'title': 'Review of Current Literature',
                      'pub_date': 'Jan 01 2024',
                      'pub_year': 2024,
                      'source': 'Journal of Reviews',
                      ...},
            '0111': {...}
             }
    """

    print('\nLoading metadata from Entrez API...')

    if not is_fill_invalid_option_allowed(fill_invalid_pmids):
        raise ValueError('fill_invalid_pmid must be either "remove" or a falsey value, like {}')

    summaries = summaries_from_pmids(pmids, email, api_key, fill_invalid_pmids=fill_invalid_pmids)
    # Clean data (inc. add defaults for fields that might not exist for some articles)
    for pmid, article in summaries.items():
        if article and (
                'DOI' not in article):  # Falsey value means invalid PMID but given default falsey value (like {})
            article['DOI'] = ''

    metadata = {}
    for pmid, article in summaries.items():
        if article:
            metadata[pmid] = {
                'title': article['Title'],
                'authors': article['AuthorList'],
                'pub_date': article['PubDate'],
                'pub_year': int(article['PubDate'][:4]),
                'source': article['Source'],
                # 'is_english': bool('English' in article['LangList']),  # Will add later anyway
                'pub_types': article['PubTypeList'],
                'is_review': bool('Review' in article['PubTypeList']),
                'doi': article['DOI'],
                'has_abstract': bool(article['HasAbstract']),
                'mesh_terms': article['mesh_terms'],
                'pub_countries': article['pub_countries'],
                'metadata': article,
            }
        elif fill_invalid_pmids == "remove":
            continue
        else:
            metadata[pmid] = article

    return metadata


def remove_invalid_pmids(pmids: list, email: str, api_key: str = None, verbose=False, return_invalid=False):
    Entrez.email = email
    if api_key is not None:
        Entrez.api_key = api_key
    max_pmids_per_call = 9999

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    returned_pmids = []
    for i_pmids in split_pmids:
        i_handle = Entrez.efetch(db="pubmed", id=gen_utils.comma_sep_str_from_list(i_pmids),
                                 rettype="xml", retmode="text")
        i_responses = Entrez.read(i_handle)
        i_responses = gen_utils.convert_to_python_obj(i_responses)
        i_handle.close()

        returned_pmids += [i['MedlineCitation']['PMID'] for i in i_responses['PubmedArticle']]

    removed_pmids = list(set(pmids) - set(returned_pmids))

    if verbose:
        if removed_pmids:
            print("\nFollowing PMIDs are not found on Entrez API and were removed:")
            for i in removed_pmids:
                print(f"\t- {i}")
            print('')

    if return_invalid:
        return returned_pmids, removed_pmids
    else:
        return returned_pmids

def get_and_parse_metadata_from_entrez(df, email, api_key=None):
    # TODO: If we end up joining this with the automation project, this is redundant and should just use
    #  entrez_utils.metadata_from_pmids() instead

    # TODO: Check out the above? Did I not need to merge this?

    pmids = list(dict.fromkeys(df['pmid'].to_list()).keys())
    metadata = metadata_from_pmids(pmids, email=email, api_key=api_key)

    known_langs = gen_utils.load_csv_to_list(os.path.join('standard_values', 'languages.csv'))
    lang_to_col_name = {i: f"is_{i}" for i in known_langs}
    with open(os.path.join("col_name_indexes", "lang_to_col_name.json"), "w") as lang_json:
        json.dump(lang_to_col_name, lang_json)
    lang_df = pd.DataFrame(False, index=df.index, columns=lang_to_col_name.values())

    all_ctrs = set()
    for md in metadata.values():
        all_ctrs.update(md["pub_countries"])
    ctr_to_col_name = {i: f"from_{i.replace(' ', '_')}" for i in all_ctrs}
    with open(os.path.join("col_name_indexes", "ctr_to_col_name.json"), "w") as ctr_json:
        json.dump(ctr_to_col_name, ctr_json)
    ctr_df = pd.DataFrame(False, index=df.index, columns=ctr_to_col_name.values())

    df = pd.concat([df, lang_df, ctr_df], axis=1)
    df["mesh_terms"] = [[]]*len(df)

    for pmid, md in metadata.items():
        idxs = df[df['pmid'] == pmid].index

        df.loc[idxs, 'title'] = md['title']
        df.loc[idxs, 'pub_year'] = md['pub_year']
        df.loc[idxs, 'journal'] = md['source']  # Full names also available in metadata dict

        for lang in md['metadata']['LangList']:
            if lang.lower() in known_langs:
                df.loc[idxs, lang_to_col_name[lang.lower()]] = True

        # OHE countries
        for ctr in md['pub_countries']:
            df.loc[idxs, ctr_to_col_name[ctr]] = True

        # List MeSH terms
        for idx in idxs:
            df.at[idx, "mesh_terms"] = md["mesh_terms"]


        # TODO: things below
        # df.loc[idxs, 'authors'] = md['']

    # df['pub_year'] = df['pub_year'].astype(int)

    return df


def get_complete_df_from_pmids(pmids:list, email: str, api_key: str=None):

    pmids, invalid_pmids = remove_invalid_pmids(pmids, email=email, api_key=api_key, verbose=True, return_invalid=True)
    metadata = metadata_from_pmids(pmids, email=email, api_key=api_key)
    text = text_from_pmids(pmids, email=email, api_key=api_key)

    pmids = pd.DataFrame(data={'pmid': pmids}, index=pmids)
    metadata = pd.DataFrame.from_dict(metadata, orient='index')
    text = pd.DataFrame(data={'text': list(text.values())}, index=list(text.keys()))

    return pd.concat([pmids, metadata, text], axis=1, join='outer')

