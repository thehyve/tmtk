import pandas as pd


class I2B2Secure:
    def __init__(self, study):
        self.study = study

        row_list = [self.build_variable_row(var) for var_id, var in study.Clinical.all_variables.items()]
        row_list.append(self.add_top_node())

        self.df = pd.DataFrame(row_list, columns=self.columns)

    def add_top_node(self):
        c_fullname = self.study.params.TOP_NODE
        c_hlevel = c_fullname.count('\\')
        c_visualattributes = 'FAS'
        c_facttablecolumn = '@'
        c_tablename = 'STUDY'
        c_columnname = 'STUDY_ID'
        c_operator = 'T'

        return pd.Series({
            'c_hlevel': c_hlevel,
            'c_fullname': c_fullname,
            'c_name': self.study.study_name,
            'c_synonym_cd': 'N',
            'c_visualattributes': c_visualattributes,
            'c_facttablecolumn': c_facttablecolumn,
            'c_tablename': c_tablename,
            'c_columnname': c_columnname,
            'c_columndatatype': 'T',
            'c_operator': c_operator,
            'c_dimcode': c_fullname,
            'm_applied_path': '@',
            'update_date': '2016-11-09 13:44:06',
            'sourcesystem_cd': self.study.study_id,
            'secure_obj_token': self.study.study_id
        })

    def build_variable_row(self, var):
        c_fullname = '{}\\{}'.format(self.study.params.TOP_NODE,
                                     var.concept_path)
        c_hlevel = c_fullname.count('\\')

        return pd.Series({
            'c_hlevel': c_hlevel,
            'c_fullname': c_fullname,
            'c_name': var.data_label,
            'c_synonym_cd': 'N',
            'c_visualattributes': var.visual_attributes,
            'c_basecode': var.concept_code,
            'c_facttablecolumn': 'CONCEPT_CD',
            'c_tablename': 'CONCEPT_DIMENSION',
            'c_columnname': 'CONCEPT_PATH',
            'c_columndatatype': 'T',
            'c_operator': 'LIKE',
            'c_dimcode': c_fullname,
            'm_applied_path': '@',
            'update_date': '1970',
            'sourcesystem_cd': self.study.study_id,
            'secure_obj_token': self.study.study_id
        })

    @property
    def columns(self):
        return ['c_hlevel',
                'c_fullname',
                'c_name',
                'c_synonym_cd',
                'c_visualattributes',
                'c_totalnum',
                'c_basecode',
                'c_metadataxml',
                'c_facttablecolumn',
                'c_tablename',
                'c_columnname',
                'c_columndatatype',
                'c_operator',
                'c_dimcode',
                'c_comment',
                'c_tooltip',
                'm_applied_path',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'valuetype_cd',
                'm_exclusion_cd',
                'c_path',
                'c_symbol',
                'i2b2_id',
                'secure_obj_token']
