from pathlib import Path

import pandas as pd

from .sheet_exceptions import MetaDataException, ValueSubstitutionError
from ...utils import Mappings


class TreeSheet:

    column_name_map = {
        'col_name': 'column name',
        'data_source': 'sheet name/file name',
        'ontology': 'ontology code',
        'data_type': 'transmart data type'
    }

    def __init__(self, df):
        lower_columns = df.columns.str.lower()
        self.level_columns = lower_columns.str.contains('level') & ~lower_columns.str.contains('metadata')
        self.meta_columns = lower_columns.str.contains('metadata')

        self.item_name_i = list(lower_columns).index(self.column_name_map['col_name'])
        self.source_name_i = list(lower_columns).index(self.column_name_map['data_source'])

        try:
            self.ontology_code_i = list(lower_columns).index(self.column_name_map['ontology'])
        except ValueError:
            self.ontology_code_i = None

        self.df = self.forward_fill_tree_sheet(df)
        self.data_sources = self.get_data_sources(lower_columns)

    def get_data_sources(self, lower_columns) -> list:
        data_source_col = lower_columns.str.contains(self.column_name_map['data_source'])
        data_sources = self.df.loc[:, data_source_col].iloc[:, 0].dropna().unique().tolist()
        return data_sources

    def forward_fill_tree_sheet(self, df):
        df.replace(r'^\s+$', pd.np.nan, regex=True, inplace=True)
        trailing_nans = df.loc[:, self.level_columns].bfill(axis=1).isnull()
        ffilled = df.loc[:, self.level_columns].ffill()
        ffilled_masked = ffilled.mask(trailing_nans, other="")
        df.loc[:, self.level_columns] = ffilled_masked

        # Fill level columns of metadata-only rows with values from the previous row
        empty_rows_df = df.loc[:, self.level_columns][(df.loc[:, self.level_columns] == '').all(axis=1)]
        for row_idx, row in empty_rows_df.iterrows():
            df.loc[row_idx, self.level_columns] = df.loc[row_idx-1, self.level_columns]

        return df

    def create_metadata_tags_file(self) -> pd.DataFrame:
        def get_path(row, columns):
            if row.notnull().all():
                fullname = '\\' + '\\'.join(self.df.loc[row.name, columns][1:])
                path_df = [fullname, row[0], row[1], row.name]
                return pd.Series(path_df)

        tag_df = pd.DataFrame()

        for tag, value in self.get_meta_columns_iter():
            level_columns = self.get_level_columns(tag)
            sub_df = self.df.loc[:, [tag, value]]

            # Skip metadata level if it contains no data
            if sub_df.isnull().all().all():
                continue

            sub_df = sub_df.loc[sub_df.notnull().all(axis=1), :]
            tag_df = tag_df.append(sub_df.apply(get_path, axis=1, args=(level_columns,)))

        # Only return df if there are rows
        if not tag_df.empty:
            tag_df.columns = Mappings.tags_header
            return tag_df

    def get_meta_columns_iter(self) -> iter:
        """ Get meta column names and generate an iterator that iterates over pairs of columns."""
        meta_columns = self.df.loc[:, self.meta_columns].columns
        if meta_columns.size % 2 > 0:
            raise MetaDataException('Meta data columns incorrect, found: {}'.format(meta_columns.tolist()))
        meta_iter = zip(meta_columns[::2], meta_columns[1::2])
        return meta_iter

    def get_level_columns(self, column_name):
        column_index = self.df.columns.get_loc(column_name)
        lower_columns = self.df.columns[:column_index].str.lower()
        level_columns = lower_columns.str.contains('level') & ~lower_columns.str.contains('metadata')
        return level_columns


class TrialVisitSheet:
    """ Concerns with the trial visits. """

    column_name_map = {
        'Label': 'name',
        'Value': 'relative_time',
        'Unit': 'time_unit'
    }

    def __init__(self, df):
        df.rename(index=None, columns=self.column_name_map, inplace=True)
        self.df = df
        self.df.set_index('name', drop=False, inplace=True)
        self.df = self.df[Mappings.trial_visits_header]


class ModifierSheet:
    """ Concerns with the modifiers. """

    modifier_column_map = {'modifier code': 'modifier_cd',
                           'modifier name': 'name_char',
                           'modifier data type': 'Data Type'
                           }

    def __init__(self, df):
        lower_columns = df.columns.str.lower()
        self.df = df
        self.df.columns = lower_columns
        self.df.rename(columns=self.modifier_column_map, inplace=True)
        self.df['modifier_path'] = self.df['modifier_cd']

        # optional values
        self.df['dimension_type'] = pd.np.NaN
        self.df['sort_index'] = pd.np.NaN

        self.df = self.df[Mappings.modifiers_header]
        self.df.set_index('modifier_cd', drop=False, inplace=True)
        self.modifier_blueprint = {}

    def set_initial_modifier_blueprint(self, df):
        for i, modifier in df.iterrows():
            value = modifier['modifier_cd']
            self.modifier_blueprint.update({
                value: {
                    'label': 'MODIFIER',
                    'data_type': value
                }
            })

    def update_modifier_blueprint(self, item):
        reference_column, data_type = item.split('@')
        d = {'label': 'MODIFIER',
             'data_type': data_type,
             'reference_column': reference_column}
        self.modifier_blueprint.update({item: d})


class ValueSubstitutionSheet:
    """ Concerns with the word mapping. """

    column_name_map = {'col_name': 'column name',
                       'data_source': 'sheet name/file name',
                       'from': 'from value',
                       'to': 'to value'
                       }

    def __init__(self, df):
        lower_columns = df.columns.str.lower()
        self.df = df.applymap(str)
        self.df.columns = lower_columns
        self._generate_word_map()

    def _generate_word_map(self):
        # TODO these lines should be removed as they are now part of the template validation
        if self.df.iloc[:, 1:3].duplicated().any():
            columns = self.df.iloc[:, 1:3].columns
            raise ValueSubstitutionError('Found duplicate mappings for COLUMN_NAME and FROM VALUE:\n{}'.
                                         format(self.df.loc[self.df[columns].duplicated(), columns]))

        map_df = self.df.copy()
        # instead of just column name use the combination of column name and file name without suffix as key
        new_col = [(col, Path(file).stem) for col, file in zip(map_df[self.column_name_map['col_name']],
                                                               map_df[self.column_name_map['data_source']])]
        map_df[self.column_name_map['col_name']] = new_col
        map_df.drop(self.column_name_map['data_source'], axis=1, inplace=True)
        map_df.set_index([self.column_name_map['col_name'], self.column_name_map['from']], inplace=True)
        map_df.columns = ['word_map']

        def get_word_map_dict(row):
            d = row.loc[row.name, :].to_dict()
            return d

        # Group together multiple mappings on the same variable
        word_map_df = map_df.groupby(level=0).apply(get_word_map_dict)
        # Convert to final structure: {('column name', 'filename'): {'word_map': {'from': 'to', 'from2': 'to2'}}}
        self.word_map = word_map_df.T.to_dict()


class OntologyMappingSheet:
    ONTOLOGY_TOP_NODE_CODE = 'ONTOLOGY'

    def __init__(self, df):
        df.iloc[:, 2] = df.iloc[:, 2].fillna(self.ONTOLOGY_TOP_NODE_CODE)
        df[Mappings.ontology_header[-1]] = None
        df.columns = Mappings.ontology_header

        # Add top node row
        self.df = df.append(
            pd.DataFrame(
                [[self.ONTOLOGY_TOP_NODE_CODE,
                  'Ontology',
                  None,
                  None]],
                columns=Mappings.ontology_header
            ), ignore_index=True
        )

    def update_study(self, study):
        study.Clinical.OntologyMapping.df = self.df


class BlueprintFile:

    def __init__(self, tree_sheet):
        self.blueprint = self._create_blueprint(tree_sheet)
        self._add_reserved_columns()

    def _create_blueprint(self, tree_sheet):
        blueprint = {}

        def _get_blueprint_entry(row):
            item_name = row[tree_sheet.item_name_i]
            file_name = row[tree_sheet.source_name_i]
            if pd.isnull(item_name):
                return
            # Remove suffix from file if there is one
            if Path(file_name).suffix:
                file_name = Path(file_name).stem

            fullname = '\\'.join(row[tree_sheet.level_columns][1:]).strip('\\')
            path, label = fullname.rsplit('\\', 1)
            bpd = dict(
                path=path,
                label=label
            )
            if tree_sheet.ontology_code_i is not None:
                if row[tree_sheet.ontology_code_i] not in (None, pd.np.nan):
                    bpd['concept_code'] = row[tree_sheet.ontology_code_i]

            blueprint[(item_name, file_name)] = bpd

        tree_sheet.df.apply(_get_blueprint_entry, axis=1)
        return blueprint

    def update_blueprint_item(self, word_map):
        """ Update existing blueprint items. """
        for key in word_map:
            self.blueprint[key].update(word_map[key])

    def update_blueprint(self, update_dict):
        """ Add a new blueprint item to the blueprint. """
        self.blueprint.update(update_dict)

    def _add_reserved_columns(self):
        """ Adds reserved column names to the blueprint. """
        reserved_d = {
            'SUBJ_ID': {
                'path': 'Subjects',
                'label': 'SUBJ_ID'
            },
            'TRIAL_VISIT': {
                'path': 'reserved_keywords',
                'label': 'TRIAL_VISIT_LABEL'
            },
            'START_DATE': {
                'path': 'reserved_keywords',
                'label': 'START_DATE'
            },
            'END_DATE': {
                'path': 'reserved_keywords',
                'label': 'END_DATE'
            }
        }

        self.blueprint.update(reserved_d)
