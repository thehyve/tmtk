from ..utils import Mappings, path_converter, ReservedKeywordException, is_not_a_value

import pandas as pd


class VarID:
    """
    Clinical variable identifier. Contains logic to convert to string for
    jstree json.
    """

    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            # highdim or tags
            if (len(args[0]) == 32 and '_' not in args[0]) or 'tags_id_' in args[0]:
                return args[0]

        return super(VarID, cls).__new__(cls)

    def __init__(self, *args):

        if len(args) == 1 and '__' in args[0]:
            l = args[0].rsplit('__', 1)
            if '_' in l[1]:
                l += l.pop(1).split('_')
            args = l

        elif len(args) == 1 and type(args[0]) == tuple:
            args = args[0]

        self.filename = args[0]
        self.column = args[1]
        self.category = args[2] if len(args) > 2 else None

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.tuple)

    def __repr__(self):
        if self.category:
            return 'VarID({!r}, {}, {})'.format(*self.tuple)
        else:
            return 'VarID({!r}, {})'.format(*self.tuple)

    def __str__(self):
        if self.category:
            return '{}__{}_{}'.format(*self.tuple)
        else:
            return '{}__{}'.format(*self.tuple)

    def __getitem__(self, key):
        return self.tuple[key]

    def __iter__(self):
        for item in self.filename, self.column, self.category:
            if item:
                yield item

    @property
    def tuple(self):
        return tuple(self)

    @property
    def parent(self):
        return self.filename, self.column

    def create_category(self, i):
        """
        Create a category ID and return it.

        :param i: Integer
        :return: new VarID
        """
        assert not self.category, 'VarID already has category.'
        return VarID(self.filename, self.column, int(i))


class Variable:
    """
    Base class for clinical variables
    """

    VIS_DATE = 'LAD'
    VIS_TEXT = 'LAT'
    VIS_NUMERIC = 'LAN'
    VIS_CATEGORICAL = 'LAC'

    def __init__(self, datafile, column: int = None, clinical_parent=None):
        self.datafile = datafile
        self.filename = datafile.name
        self.column = column
        self._zero_column = column - 1
        self.parent = clinical_parent

    def __repr__(self):
        return '{} {!r}: {}'.format(self.__class__.__name__,
                                    self.var_id,
                                    self.concept_path)

    @property
    def values(self):
        """

        :return: All values as found in the datafile.
        """
        return self.datafile.df.iloc[:, self._zero_column]

    @values.setter
    def values(self, series: pd.Series):
        self.datafile.df.iloc[:, self._zero_column] = series

    @property
    def unique_values(self):
        """

        :return: Unique set of values in the datafile.
        """
        return self.values.unique()

    @property
    def var_id(self):
        """

        :return: Variable identifier tuple (datafile.name, column).
        """
        return VarID(self.datafile.name, self.column)

    @property
    def is_numeric_in_datafile(self):
        """
        True if the datafile contains only numerical items.

        :return: bool.
        """
        try:
            set(map(float, self.values))
            return True
        except (ValueError, TypeError):
            return False

    @property
    def min(self):
        if self.is_numeric_in_datafile:
            return min(set(map(float, self.values)))

    @property
    def max(self):
        if self.is_numeric_in_datafile:
            return max(set(map(float, self.values)))

    @property
    def is_numeric(self):
        """
        True if transmart-batch will load this concept as numerical. This includes
        information from word mapping and column mapping.

        :return: bool.
        """
        if self.forced_categorical:
            return False

        if not self.is_in_wordmap:
            return self.is_numeric_in_datafile
        else:
            try:
                set(map(float, self.mapped_values))
                return True
            except (ValueError, TypeError):
                return False

    @property
    def is_empty(self):
        """
        Check if variable is fully empty.

        :return: bool.
        """
        return self.values.apply(is_not_a_value).all()

    @property
    def concept_path(self):
        """
        Concept path after conversions by transmart-batch. Combination
        of self.category_code and self.data_label. Cannot be set.

        :return: str.
        """
        cp = self.parent.ColumnMapping.get_concept_path(self.var_id)
        return path_converter(cp)

    @property
    def category_code(self):
        """
        The second column of the column mapping file for this variable.
        This combines with self.data_label to create self.concept_path.

        :return: str.
        """
        return self.parent.ColumnMapping.select_row(self.var_id)[1]

    @category_code.setter
    def category_code(self, value):
        self.parent.ColumnMapping.set_concept_path(self.var_id, path=value)

    @property
    def column_map_data(self):
        """Column mapping row as dictionary where keys are short descriptors.

        :return: dict.
        """
        row = self.parent.ColumnMapping.select_row(self.var_id)

        data_args = {}
        for i, s in enumerate(Mappings.column_mapping_s):
            data_args.update({s: row[i] if len(row) > i else None})
        return data_args

    @property
    def data_label(self):
        """
        Variable data label.

        :return: str.
        """
        return self.parent.ColumnMapping.select_row(self.var_id)[3]

    @data_label.setter
    def data_label(self, value):
        self.parent.ColumnMapping.set_concept_path(self.var_id, label=value)

    @property
    def word_map_dict(self):
        """
        A dictionary with word mapped categoricals. Keys are items in the datafile,
        values are what they will be mapped to through the word mapping file. Unmapped
        items are also added as key, value pair.

        :return: dict.
        """
        values = set(self.values)
        d = dict(zip(values, values))
        d.update(self.parent.WordMapping.get_word_map(self.var_id))
        return d

    @word_map_dict.setter
    def word_map_dict(self, d):
        self.parent.WordMapping.set_word_map(self.var_id, d)

    @property
    def mapped_values(self):
        """
        Data items after word mapping.

        :return: list.
        """
        if self.is_in_wordmap:
            return self.values.map(self.word_map_dict)
        else:
            return self.values

    @property
    def forced_categorical(self):
        """Check if forced categorical by entering 'CATEGORICAL' in data type column.
        Can be changed by setting this to True or False.

        :return: bool.
        """
        return self.column_type == 'CATEGORICAL'

    @forced_categorical.setter
    def forced_categorical(self, value: bool):
        self.column_type = 'CATEGORICAL' if bool(value) else ''

    @property
    def is_in_wordmap(self):
        """
        Check if variable is represented in word mapping file.

        :return: bool.
        """
        return tuple(self.var_id) in self.parent.WordMapping.df.index
    
    def word_mapped_not_present(self):
        """
        Gets the values that are in the word map but not in the data file.

        :return: set.
        """
        if not self.is_in_wordmap:
            return set()

        mapped_value_column = self.parent.WordMapping.df.columns[2]

        t_index = tuple(self.var_id)
        mapped_values = self.parent.WordMapping.df.loc[t_index, mapped_value_column]

        if type(mapped_values) != str:
            mapped_values = set(mapped_values)
        else:
            mapped_values = {mapped_values}

        return mapped_values - set(self.values)

    @property
    def header(self):
        return self.datafile.df.columns[self._zero_column]

    @property
    def visual_attributes(self):

        if self.column_type == 'DATE':
            return self.VIS_DATE
        elif self.column_type == 'TEXT':
            return self.VIS_TEXT
        elif self.is_numeric:
            return self.VIS_NUMERIC
        else:
            return self.VIS_CATEGORICAL

    @property
    def reference_column(self):
        return self.parent.ColumnMapping.select_row(self.var_id)[4]

    @reference_column.setter
    def reference_column(self, value):
        self.parent.ColumnMapping.set_reference_column(self.var_id, value)

    @property
    def concept_code(self):
        return self.parent.ColumnMapping.select_row(self.var_id)[5]

    @concept_code.setter
    def concept_code(self, value):
        self.parent.ColumnMapping.set_concept_code(self.var_id, value)

    @property
    def column_type(self):
        """
        Column data type setting can be found in modifiers file for MODIFIER vars,
        else it is in the DataType column of column mapping. If it is not found, it will
        be either numerical or categorical based on the datafile values.
        """
        if self.data_label == 'MODIFIER':
            return self.parent.Modifiers.df.loc[self.modifier_code, self.parent.Modifiers.df.columns[3]]
        else:
            try:
                return self.parent.ColumnMapping.select_row(self.var_id)[6]
            except IndexError:
                return None

    @column_type.setter
    def column_type(self, value):
        self.parent.ColumnMapping.set_column_type(self.var_id, value)

    @property
    def modifier_code(self):
        """ Requires implementation, always returns '@'."""
        return self.parent.ColumnMapping.select_row(self.var_id)[6] if self.data_label == 'MODIFIER' else '@'

    def _get_all(self, label: str):
        """
        Will look for keyword variables in the same data file based a label and
        check whether it applies to self. The reference column can be used to
        specify to which columns a keyword applies. Providing a comma separated
        list of column indices is supported.

        :param str label: data label.
        :return list: a list of variables.
        """
        vars_ = self.parent.find_variables_by_label(label, self.var_id.filename)
        inclusion_criteria = (None, pd.np.nan, '')
        return [var for var in vars_
                if var.reference_column in inclusion_criteria
                or str(self.column) in str(var.reference_column).split(',')]

    def _get_one_or_none(self, label: str):
        """
        Will look for a keyword variable that applies to self. Will raise
        ReservedKeywordException if more than 1 is found.

        :param str label: data label.
        :return: variable.
        """
        vars_ = self._get_all(label)
        if len(vars_) > 2:
            raise ReservedKeywordException('Multiple {} found for {}'.format(label, self))
        elif vars_:
            return vars_[0]

    @property
    def subj_id(self):
        subj_id = self._get_one_or_none('SUBJ_ID')
        if subj_id:
            return subj_id
        else:
            raise ReservedKeywordException('No SUBJ_ID found for {}'.format(self))

    @property
    def start_date(self):
        return self._get_one_or_none('START_DATE')

    @property
    def end_date(self):
        return self._get_one_or_none('END_DATE')

    @property
    def trial_visit(self):
        return self._get_one_or_none('TRIAL_VISIT_LABEL')

    @property
    def modifiers(self):
        """
        Returns a list of all modifier variable that apply to this variable.
        The data label for these variables have to be 'MODIFIER' and the
        fifth column (reference column) has to either be empty or the column
        this variable has.

        :return: list of modifier variables.
        """
        return self._get_all('MODIFIER')

