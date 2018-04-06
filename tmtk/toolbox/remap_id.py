import pandas as _pd


def _match_response_with_query(response_table, query, target):
    """
    Private method that gets the right response value for a query.

    :param response_table: the response table from mygene.info
    :param query: the value to search on (e.g. hgnc gene symbol).
    :param target: column name that has the id to map to.
    :return: a corresponding id.
    """
    try:
        r = response_table.loc[query]
        try:
            return r.get_value(target)
        except TypeError:
            sorted_r = r.sort_values('_score', ascending=False)
            return sorted_r[target].iloc[0]

    except (KeyError, TypeError):
        pass
    return _pd.np.nan


def hgnc_to_entrez(iterable):
    """
    Give this an iterable with HGNC gene symbols and convert them to Entrez
    Gene IDs.

    :param iterable: HGNC gene symbols.
    :return: pd.Series with equal number of corresponding gene symbols.
    """
    import mygene as _mygene

    _mg = _mygene.MyGeneInfo()

    target = 'entrezgene'

    input_iterable = iterable

    try:
        iterable = iterable.unique()
    except AttributeError:
        pass

    out = _mg.querymany(iterable,
                        scopes=['symbol', 'alias'],
                        fields=target,
                        species='human',
                        as_dataframe=True)

    mgidf = out.loc[out.entrezgene.notnull()].copy()
    # remove '.0' from IDs and convert to string. Mygene should be improved to return entrez ids as string.
    mgidf.loc[:, target] = mgidf.loc[:, target].astype(int).astype(str)
    return _pd.Series(input_iterable).apply(lambda x: _match_response_with_query(mgidf, x, target))

