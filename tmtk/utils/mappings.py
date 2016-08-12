class Mappings:
    """
    Collection of statics used in various parts of the code.
    """

    # Column Mapping file
    filename = 'Filename'
    cat_cd = 'Category Code'
    col_num = 'Column Number'
    data_label = 'Data Label'
    magic_5 = 'Magic 5th'
    magic_6 = 'Magic 6th'
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

    # Path delimeter used for paths.
    PATH_DELIM = '\u2215'  # Mathematical division sign

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

    @staticmethod
    def get_params(dtype=None):
        """
        Return mapping for params classes.  Return only for datatype
        if dtype is set.  Else return full map.

        :param dtype: optional datatype (e.g. cnv)
        :return: dict with mapping, or class.
        """
        from ..params.HighDimParams import HighDimParams
        from ..params.TagsParams import TagsParams
        from ..params.StudyParams import StudyParams
        from ..params.ClinicalParams import ClinicalParams
        from ..params.AnnotationParams import AnnotationParams

        map_d = {'rnaseq': HighDimParams,
                 'rnaseq_annotation': AnnotationParams,
                 'cnv': HighDimParams,
                 'cnv_annotation': AnnotationParams,
                 'proteomics': HighDimParams,
                 'proteomics_annotation': AnnotationParams,
                 'expression': HighDimParams,
                 'mrna_annotation': AnnotationParams,
                 'tags': TagsParams,
                 'study': StudyParams,
                 'clinical': ClinicalParams,
                 'mirna': HighDimParams,
                 'mirna_annotation': AnnotationParams,
                 }

        if dtype:
            return map_d[dtype]
        else:
            return map_d

    @staticmethod
    def get_annotations(dtype=None):
        """
        Return mapping for annotations classes.  Return only for datatype
        if dtype is set.  Else return full map.

        :param dtype: optional datatype (e.g. cnv_annotation)
        :return: dict with mapping, or class.
        """
        from ..annotation.ChromosomalRegions import ChromosomalRegions
        from ..annotation.MicroarrayAnnotation import MicroarrayAnnotation
        from ..annotation.ProteomicsAnnotation import ProteomicsAnnotation
        from ..annotation.MirnaAnnotation import MirnaAnnotation

        map_d = {'microarray_annotation': MicroarrayAnnotation,
                 'cnv_annotation': ChromosomalRegions,
                 'rnaseq_annotation': ChromosomalRegions,
                 'proteomics_annotation': ProteomicsAnnotation,
                 'annotation': MicroarrayAnnotation,
                 'mrna_annotation': MicroarrayAnnotation,
                 'mirna_annotation': MirnaAnnotation,
                 }

        if dtype:
            return map_d[dtype]
        else:
            return map_d

    @staticmethod
    def get_highdim(dtype=None):
        """
        Return mapping for high dimensional classes.  Return only for datatype
        if dtype is set.  Else return full map.

        :param dtype: optional datatype (e.g. cnv)
        :return: dict with mapping, or class.
        """
        from ..highdim.CopyNumberVariation import CopyNumberVariation
        from ..highdim.ReadCounts import ReadCounts
        from ..highdim.Expression import Expression
        from ..highdim.Mirna import Mirna
        from ..highdim.Proteomics import Proteomics

        map_d = {'rnaseq': ReadCounts,
                 'cnv': CopyNumberVariation,
                 'expression': Expression,
                 'proteomics': Proteomics,
                 'mirna': Mirna,
                 }
        if dtype:
            return map_d[dtype]
        else:
            return map_d
