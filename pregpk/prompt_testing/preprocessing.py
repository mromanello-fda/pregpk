import random


def make_article_queries(dataset):
    # TODO: maybe clean this up as well
    section_key = {"title": "<TITLE>: ",
                   "abstract": "<ABSTRACT>: ",
                   "intro": "<INTRODUCTION>: ",
                   "methods": "<METHODS>: ",
                   "results": "<RESULTS>: ",
                   "fig": "<FIGURE CAPTIONS>: ",
                   "table": "<TABLE CAPTIONS>: ",
                   "discuss": "<DISCUSSION>: ",
                   "concl": "<CONCLUSION>: ",
                   "abbr": "<ABBREVIATIONS>: ",
                   }

    # dataset["query"] = dataset.apply(lambda x: f"<TITLE>: {x['title']} <ABSTRACT>: {x['abstract']}", axis=1)
    # dataset["query"] = dataset.apply(
    #     lambda x: '\n'.join([f"{section_key[sec]}" for sec in x]),
    #     axis=0)

    for idx, row in dataset.iterrows():
        row = row.dropna()
        sections = [i for i in row.index.to_list() if i != "has_pk_data"]
        dataset.loc[idx, "query"] = ' '.join([f"{section_key[sec]}{row[sec]}" for sec in sections])

    return dataset


def test_set_from_full_dataset(dataset, test_set_params, random_seed=None):
    # TODO: Maybe split up into functions
    # TODO: Add token limit instead of n size? Would need actual text and query before.

    test_set_params.setdefault("balance_classes", False)
    test_set_params.setdefault("n", None)

    idx_test_set = dataset.index.tolist()

    if random_seed is not None:
        random.seed(random_seed)

    if test_set_params["balance_classes"]:
        class_groups = dataset.groupby(["has_pk_data"])
        n_min_class = min([len(i) for i in class_groups.groups.values()])

        idx_test_set = []
        for i_class_index in class_groups.groups.values():
            idx_test_set += random.sample(i_class_index.tolist(), n_min_class)

    n = test_set_params["n"]
    if n is not None:
        if test_set_params["balance_classes"]:
            if n % 2 != 0:
                n = n - 1
            idx_test_set = random.sample(idx_test_set[:len(idx_test_set)//2], n//2) + \
                           random.sample(idx_test_set[len(idx_test_set)//2:], n//2)
        else:
            idx_test_set = random.sample(idx_test_set, n)

    return dataset.loc[idx_test_set]
