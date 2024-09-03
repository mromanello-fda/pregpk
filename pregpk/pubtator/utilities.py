import warnings
import requests
import time
import json
from tqdm import tqdm
import pandas as pd
from pregpk import gen_utils


def is_fill_invalid_option_allowed(fill_invalid_val):  # Must either be "remove" or falsey value
    return (fill_invalid_val == 'remove') or not fill_invalid_val


def api_call_from_pmids(pmids: list) -> str:
    """
    Creates PubTator 3 API query for full text data from list of PMIDs.
    :param pmids: list of PMIDs
    :return: string used to query full-text information from PubTator API
    """
    pmids_str = gen_utils.comma_sep_str_from_list(pmids)
    return f"https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson?pmids={pmids_str}&full=true"


def text_from_pmids(pmids: list, fill_invalid_pmids='remove') -> dict:
    """
    Fetches all text available from PubTator 3 API for a list of PMIDs. Returned text is split into sections (title,
    abstract, methods, etc.).
    :param pmids: list of PMID strings to obtain texts from PubTator 3
    :return: nested dict where PMIDs (keys) map onto a dictionary containing sections of text returned from PubTator.
        eg. {'1234':
                {'title': 'Review of Current Literature',
                 'abstract':'We present a review of current literature.'
                 'methods': 'We reviewed all the literature on PubMed.',
                 'discuss': 'There have been a lot of advancements to the field but still several limitations',
                 },
             '0111':
                {...}
            }
    """

    if not is_fill_invalid_option_allowed(fill_invalid_pmids):
        raise ValueError('fill_invalid_pmid must be either "remove" or a falsey value, like None or {}')

    print('\nLoading available full text data from PubTator API...')
    time.sleep(0.1)  # For some reason print statement showing up after first tqdm loading bar

    min_request_dt = 0.3
    last_req_t = time.time() - min_request_dt*2
    max_pmids_per_call = 99

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    texts = {}

    for i_pmids in tqdm(split_pmids):
        time.sleep(max(0.3 - (time.time() - last_req_t), 0))  # Not supersede PubTator maximum calls per second
        last_req_t = time.time()  # Have to set before the request (since the request is what takes longest per iter)
        resp = requests.get(api_call_from_pmids(i_pmids))

        if resp.status_code == 200:  # Successful request
            # articles = [json.loads(i) for i in resp.text.split('\n') if i]  # OLD API FORMAT "if i" to remove falsey values (empty string)
            if resp.text:  # resp.text will return falsey '' if only pmids without text are queried
                articles = json.loads(resp.text)['PubTator3']
            else:
                continue  # Move on to next i_pmids

            for art in articles:
                art['pmid'] = str(art['pmid'])
                art_text = {}  # List of sections returned
                for passage in art['passages']:
                    if passage['text']:  # Only if passage actually has text, not an empty string
                        try:
                            section = passage['infons']['section_type'].lower()
                        except KeyError:  # Probably because only title and abstract
                            section = passage['infons']['type']
                        except:
                            warnings.warn(f"PubTator return for PMID {art['pmid']} does not have 'section_type' or "
                                          f"'type' fields as expected.")
                            texts[art['pmid']] = {}
                            continue

                        if section not in art_text:  # Add section if not yet in dictionary
                            art_text[section] = ''
                        art_text[section] += passage['text'] + ' '

                for sec in art_text.keys():
                    art_text[sec] = art_text[sec][:-1]  # Delete final space

                texts[art['pmid']] = art_text

    # Add text for any pmids that were not returned by PubTator
    removed_pmids = set(pmids) - set(texts.keys())
    if removed_pmids and fill_invalid_pmids != 'remove':
        texts.update({i: fill_invalid_pmids for i in removed_pmids})

    return texts


def metadata_from_pmids(pmids: list, fill_invalid_pmids='remove') -> dict:

    if not is_fill_invalid_option_allowed(fill_invalid_pmids):
        raise ValueError('fill_invalid_pmid must be either "remove" or a falsey value, like None or {}')

    print('\nLoading metadata from PubTator API...')

    min_request_dt = 0.3
    last_req_t = time.time() - min_request_dt*2
    max_pmids_per_call = 99

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    metadata = {}
    for i_pmids in tqdm(split_pmids):
        time.sleep(max(0.3 - (time.time() - last_req_t), 0))  # Not supersede PubTator maximum calls per second
        last_req_t = time.time()  # Have to set before the request (since the request is what takes longest per iter)
        resp = requests.get(api_call_from_pmids(i_pmids))

        # articles = [json.loads(i) for i in resp.text.split('\n') if i]  # OLD API FORMAT "if i" to remove falsey values (empty string)
        if resp.text:  # resp.text will return falsey '' if only pmids without text are queried
            articles = json.loads(resp.text)['PubTator3']
        else:
            continue

        for art in articles:
            # Get abstract
            has_abstract = False
            for ipassage in art['passages']:
                if ipassage['infons']['type'] == 'abstract':
                    has_abstract = True
                    break
            # Get DOI
            art_doi = get_doi_from_article_dict(art)
            metadata[str(art['pmid'])] = {
                'title': art['passages'][0]['text'],
                'authors': art['authors'],
                'pub_date': art['date'][:art['date'].index('T')], # Only date, not time (string in format YYYY-MM-DDTHH:MM:SSZ
                'pub_year': int(art['date'][:4]),
                'source': art['journal'],
                'doi': art_doi,
                'has_abstract': has_abstract,
            }

    # Add text for any pmids that were not returned by PubTator
    removed_pmids = set(pmids) - set(metadata.keys())
    if removed_pmids and fill_invalid_pmids != 'remove':
        metadata.update({i: fill_invalid_pmids for i in removed_pmids})

    return metadata


def get_doi_from_article_dict(article:dict):

    if gen_utils.nested_keys_exists(article, 'passages', 0, 'infons', 'article-id_doi'):
        return article['passages'][0]['infons']['article-id_doi']

    if gen_utils.nested_keys_exists(article, 'passages', 0, 'infons', 'journal'):
        if 'doi:' in article['passages'][0]['infons']['journal']:
            journal_string = article['passages'][0]['infons']['journal']
            return journal_string[journal_string.index('doi:')+4:].rstrip('.')

    return ''


def remove_invalid_pmids(pmids:list, verbose=False, return_invalid=False):

    min_request_dt = 0.3
    last_req_t = time.time() - min_request_dt * 2
    max_pmids_per_call = 99

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    returned_pmids = []
    for i_pmids in split_pmids:
        time.sleep(max(0.3 - (time.time() - last_req_t), 0))  # Not supersede PubTator maximum calls per second
        last_req_t = time.time()  # Have to set before the request (since the request is what takes longest per iter)
        resp = requests.get(api_call_from_pmids(i_pmids))

        if not resp.text:  # If all pmids are invalid
            continue
        else:
            returned_pmids += [str(i['pmid']) for i in json.loads(resp.text)['PubTator3']]

    removed_pmids = list(set(pmids) - set(returned_pmids))

    if verbose:
        if removed_pmids:
            print("\nFollowing PMIDs are not found on PubTator API and were removed:")
            for i in removed_pmids:
                print(f"\t- {i}")
            print('')

    if return_invalid:
        return returned_pmids, removed_pmids
    else:
        return returned_pmids


def get_complete_df_from_pmids(pmids):

    pmids, invalid_pmids = remove_invalid_pmids(pmids, verbose=True, return_invalid=True)
    metadata = metadata_from_pmids(pmids)
    text = text_from_pmids(pmids)

    pmids = pd.DataFrame(data={'pmid':pmids}, index=pmids)
    metadata = pd.DataFrame.from_dict(metadata, orient='index')
    text = pd.DataFrame(data={'text': list(text.values())}, index=list(text.keys()))

    return pd.concat([pmids, metadata, text], axis=1, join='outer')
