from ..utils import Mappings, path_converter, is_numeric


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

    def __init__(self, datafile, column: int = None, clinical_parent=None):
        self.datafile = datafile
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
        return self.datafile.df.ix[:, self._zero_column]

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
        except ValueError:
            return False

    @property
    def is_numeric(self):
        """
        True if transmart-batch will load this concept as numerical. This includes
        information from word mapping and column mapping.

        :return: bool.
        """
        if self.forced_categorical:
            return False
        if not self.is_in_wordmap and self.is_numeric_in_datafile:
            return True
        else:
            return is_numeric(self.mapped_values)

    @property
    def is_empty(self):
        """
        Check if variable is fully empty.

        :return: bool.
        """
        return not self.values.any(skipna=True)

    @property
    def concept_path(self):
        """
        Concept path after conversions by transmart-batch.

        :return: str.
        """
        cp = self.parent.ColumnMapping.get_concept_path(self.var_id)
        cp = path_converter(cp)
        return cp.replace('_', ' ')

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
        return self.column_map_data.get(Mappings.data_label_s)

    @property
    def word_map_dict(self):
        """
        A dictionary with word mapped categoricals. Keys are items in the datafile,
        values are what they will be mapped to through the word mapping file.  Unmapped
        items are also added as key, value pair.

        :return: dict.
        """
        values = self.values
        d = dict(zip(values, values))
        d.update(self.parent.WordMapping.get_word_map(self.var_id))
        return d

    @property
    def mapped_values(self):
        """
        Data items after word mapping.

        :return: list.
        """
        return [v for k, v in self.word_map_dict.items()]

    @property
    def forced_categorical(self):
        """Check if forced categorical by entering 'CATEGORICAL' in 7th column.

        :return: bool.
        """
        return self.column_map_data.get(Mappings.concept_type_s) == 'CATEGORICAL'

    def validate(self, verbosity=2):
        pass

    @property
    def is_in_wordmap(self):
        """
        Check if variable is represented in word mapping file.

        :return: bool.
        """
        return tuple(self.var_id) in self.parent.WordMapping.df.index
