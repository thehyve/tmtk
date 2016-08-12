import pandas as pd


def remap_chromosomal_regions(origin_platform=None, destination_platform=None, datafile=None,
                              flag_indicator='.flag', to_dest=2, start_dest=3, end_dest=4,
                              region_dest=1, chr_origin=2, start_origin=3, end_origin=4,
                              region_origin=1, region_data=0):
    dest_regions = destination_platform.ix[:, [to_dest, start_dest, end_dest]]
    dest_regions = _convert_xy_to_int(dest_regions)

    orig_regions = origin_platform.ix[:, [chr_origin, start_origin, end_origin]]
    orig_regions = _convert_xy_to_int(orig_regions)

    # Find overlapping regions
    overlap = _map_multiple_segments_to_gene(dest_regions, orig_regions)

    segments_region_column = datafile.columns[region_data]
    flag_columns = _find_flag_columns(datafile, flag_indicator)

    # Remove any regions without mapping
    only_scores = overlap[~overlap.isnull()]

    # Get region ids corresponding to the mapping
    region_id_mapping = only_scores.apply(lambda x: map_index_to_region_ids(x,
                                                                            origin_platform,
                                                                            region_origin))
    # Find the mean value across the mapped regions
    remapped_regions = region_id_mapping.apply(lambda x: return_mean(datafile, x, flag_columns))

    # Create a new data structure with the
    new_df = pd.DataFrame(columns=datafile.columns, data=remapped_regions)

    # Add back the region id's
    new_df[segments_region_column] = destination_platform.ix[:, region_origin]

    # Convert flag columns to int
    if any(flag_columns):
        new_df[flag_columns] = new_df[flag_columns].applymap(int)

    return new_df


def _find_flag_columns(datafile, flag_indicator):
    """

    :param datafile:
    :param flag_indicator: pattern to look for flag column
    :return: list with columns or None
    """
    col_names_contain_flag = datafile.columns.str.contains(flag_indicator)
    if sum(col_names_contain_flag) > 0:  # if a flag column found, return list with
        flag_columns = datafile.columns[col_names_contain_flag]
        return flag_columns
    else:
        return pd.Series([])


def _convert_xy_to_int(df):
    df = df.replace(to_replace='X', value=23)
    df = df.replace(to_replace='Y', value=24)
    df = df.applymap(int)
    return df


def _find_overlapping_segments(chrom, start, end, regions):
    which = (regions.ix[:, 0] == chrom) & (regions.ix[:, 2] >= start) & (regions.ix[:, 1] <= end)
    selected_segments_index = regions.loc[which].index
    if len(selected_segments_index) > 0:
        return list(selected_segments_index)
    else:
        return None


def _map_multiple_segments_to_gene(from_regions, to_regions):
    overlap = from_regions.apply(lambda x: _find_overlapping_segments(x.iloc[0],
                                                                      x.iloc[1],
                                                                      x.iloc[2],
                                                                      to_regions), axis=1)
    return overlap


def map_index_to_region_ids(gene, origin_platform, region_origin):
    mappings = []
    for i in gene:
        mappings += [origin_platform.ix[i, region_origin]]
    return mappings


def return_mean(datafile, mapping, flag_columns=None):
    mapped_regions = pd.DataFrame(datafile[datafile.ix[:, 0].isin(mapping)])
    mean_values = mapped_regions.ix[:, 1:].applymap(float).mean()
    if flag_columns.any() and (len(mapping) > 1):
        mean_values[flag_columns] = (datafile[datafile.ix[:, 0].isin(mapping)][flag_columns]
                                     ).apply(lambda x: pd.value_counts(x).index[0])
    return mean_values
