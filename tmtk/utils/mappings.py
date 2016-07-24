class Mappings:
    """
    Collection of statics used in various parts of the code.
    """

    # Column Mapping file
    filename = 'Filename'
    cat_cd = 'Category Code'
    col_num = 'Column Number'
    data_label = 'Data Label'
    magic_5 = 'Data Label Source'
    magic_6 = 'Control Vocab Cd'
    concept_type = 'Concept Type'

    # Tags
    tags_path = 'Concept Path'
    tags_title = 'Title'
    tags_description = 'Description'
    tags_weight = 'Weight'
    tags_node_name = 'Tags'

    # Word mapping file
    df_value = 'Datafile Value'
    map_value = 'Mapping Value'

    # Jstree json ids
    filename_s = 'fn'
    cat_cd_s = 'ccd'
    col_num_s = 'col'
    data_label_s = 'dl'
    magic_5_s = 'm5'
    magic_6_s = 'm6'
    concept_type_s = 'cty'

    df_value_s = 'dfv'
    map_value_s = 'map'

    column_mapping_header = [filename,
                             cat_cd,
                             col_num,
                             data_label,
                             magic_5,
                             magic_6,
                             concept_type,
                             ]

    column_mapping_s = [filename_s,
                        cat_cd_s,
                        col_num_s,
                        data_label_s,
                        magic_5_s,
                        magic_6_s,
                        concept_type_s,
                        ]

    word_mapping_header = [filename,
                           col_num,
                           df_value,
                           map_value,
                           ]

    tags_header = [tags_path,
                   tags_title,
                   tags_description,
                   tags_weight]

    params = {'rnaseq': 'HighDimParams',
              'cnv': 'HighDimParams',
              'proteomics': 'HighDimParams',
              'expression': 'HighDimParams',
              'tags': 'TagsParams',
              'study': 'StudyParams',
              'clinical': 'ClinicalParams',
              'mirna': 'HighDimParams',
              }

    annotations = {'microarray_annotation': 'MicroarrayAnnotation',
                   'cnv_annotation': 'ChromosomalRegions',
                   'rnaseq_annotation': 'ChromosomalRegions',
                   'proteomics_annotation': 'ProteomicsAnnotation',
                   'annotation': 'MicroarrayAnnotation',
                   'mrna_annotation': 'MicroarrayAnnotation',
                   'mirna_annotation': 'MirnaAnnotation',
                   }

    highdim = {'rnaseq': 'ReadCounts',
               'cnv': 'CopyNumberVariation',
               'expression': 'Expression',
               'proteomics': 'Proteomics',
               'mirna': 'Mirna',
               }

    path_delim = '|'
