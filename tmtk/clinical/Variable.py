from ..utils import Mappings, path_converter, is_numeric


class VariableCollection:
    def __init__(self, clinical_parent=None):
        """
        Collection of Variables. Add datafiles or single variables. Get by variable id_.
        """
        self.parent = clinical_parent

    def get(self, var_id):
        """
        Return a Variable object based on var_id.
        :param var_id:
        :return:
        """
        df_name, column = var_id
        datafile = self.parent.get_datafile(df_name)
        return Variable(datafile, column, self.parent)

    @property
    def all(self):
        return self.parent.ColumnMapping.ids

    def get_all(self):
        return {var_id: self.get(var_id) for var_id in self.all}


class Variable:
    """
    Base class for clinical variables
    """
    def __init__(self, datafile, column: int =None, clinical_parent=None):
        self.datafile = datafile
        self.column = column
        self._zero_column = column - 1
        self.parent = clinical_parent

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__,
                               self.concept_path)

    @property
    def values(self):
        return self.datafile.df.ix[:, self._zero_column]

    @property
    def unique_values(self):
        return self.values.unique()

    @property
    def id_(self):
        return self.datafile.name, self.column

    @property
    def is_numeric_in_datafile(self):
        try:
            list(map(float, self.values))
            return True
        except ValueError:
            return False

    @property
    def is_numeric(self):
        if self.forced_categorical:
            return False
        if not self.is_in_wordmap and self.is_numeric_in_datafile:
            return True
        else:
            return is_numeric(self.mapped_values)

    @property
    def is_empty(self):
        return not self.values.any(skipna=True)

    @property
    def concept_path(self):
        """
        Returns concept converted as expected in transmart
        :return:
        """
        cp = self.parent.ColumnMapping.get_concept_path(self.id_)
        cp = path_converter(cp)
        return cp.replace('_', ' ')

    @property
    def column_map_data(self):
        row = self.parent.ColumnMapping.select_row(self.id_)

        data_args = {}
        for i, s in enumerate(Mappings.column_mapping_s):
            data_args.update({s: row[i] if len(row) > i else None})
        return data_args

    @property
    def data_label(self):
        return self.column_map_data.get(Mappings.data_label_s)

    @property
    def word_map_dict(self):
        """
        A dictionary with word mapped variables. Keys are values in the datafile,
        values are what they will be mapped to (through word mapping file)
        :return: dict
        """
        word_map = self.parent.WordMapping.get_word_map(self.id_)
        return {v: word_map.get(v, v) for v in self.unique_values}

    @property
    def mapped_values(self):
        return [v for k, v in self.word_map_dict.items()]

    @property
    def forced_categorical(self):
        return self.column_map_data.get(Mappings.concept_type_s) == 'CATEGORICAL'

    def validate(self, verbosity=2):
        pass

    @property
    def is_in_wordmap(self):
        return bool(len(self.parent.WordMapping.get_word_map(self.id_)))
