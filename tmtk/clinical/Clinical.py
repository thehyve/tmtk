import os
from pathlib import Path

import pandas as pd

import tmtk
from .ColumnMapping import ColumnMapping
from .DataFile import DataFile
from .Ontology import OntologyMapping
from .Variable import Variable, VarID
from .WordMapping import WordMapping
from .modifier import Modifiers
from .trial_vists import TrialVisits
from ..utils import PathError, clean_for_namespace, FileBase, ValidateMixin, path_converter, BlueprintException
from ..utils.batch import TransmartBatch


class Clinical(ValidateMixin):
    """
    Container class for all clinical data related objects, i.e. the column
    mapping, word mapping, and clinical data files.

    This object has methods that add data files, and for lookups of clinical
    files and variables.
    """

    def __init__(self, clinical_params=None):
        self._ColumnMapping = None
        self.WordMapping = None
        self.OntologyMapping = None
        self.Modifiers = None
        self.TrialVisits = None
        self._params = clinical_params

    def __str__(self):
        return "ClinicalObject ({})".format(self.params.path)

    def __repr__(self):
        return "ClinicalObject ({})".format(self.params.path)

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value
        self.ColumnMapping = ColumnMapping(params=self.params)
        self.WordMapping = WordMapping(params=self.params)

        if not tmtk.options.transmart_batch_mode:
            self.OntologyMapping = OntologyMapping(params=self.params)
            self.Modifiers = Modifiers(params=self.params)
            self.TrialVisits = TrialVisits(params=self.params)

    @property
    def ColumnMapping(self):
        return self._ColumnMapping

    @ColumnMapping.setter
    def ColumnMapping(self, value):
        self._ColumnMapping = value
        for file in self.ColumnMapping.included_datafiles:
            clinical_data_path = os.path.join(self.params.dirname, file)
            self.add_datafile(clinical_data_path)

    def apply_blueprint(self, blueprint, omit_missing=False):
        """
        Update the column mapping by applying a template.

        :param blueprint: expected input is a dictionary where keys are column names
            as found in clinical datafiles. Each column header name has a dictionary
            describing the path and data label and other information. For example:

            {
              "GENDER": {
                "path": "Characteristics\\Demographics",
                "label": "Gender",
                "concept_code": "SNOMEDCT/263495000",
                "metadata_tags": {
                  "Info": "As measured when born."
                },
                "force_categorical": "Y",
                "word_map": {
                  "goo": "values",
                  "pile": "list"
                },
                "expected_categorical": [
                  "pile",
                  "of",
                  "goo"
                ]
              },
              "BPBASE": {
                "path": "Lab results\\Blood",
                "label": "Blood pressure (baseline)",
                "expected_numerical": {
                  "min": 1,
                  "max": 9
                }
              }
            }
        :param omit_missing: if True, then variable that are not present in the blueprint
        will be set to OMIT.
        """
        for variable in self.all_variables.values():
            # The default blueprint key is a tuple containing the column name and the file name (without extension)
            blueprint_key = (variable.header.strip(), Path(variable.filename).stem)
            if blueprint_key not in blueprint:
                # Fallback to assuming a column-name-only key
                blueprint_key = blueprint_key[0]

            blueprint_var = blueprint.get(blueprint_key)

            if not blueprint_var:
                self.msgs.info("Column with header {!r}. Not found in blueprint.".format(variable.header))
                if omit_missing:
                    variable.data_label = 'OMIT'
                continue

            if blueprint_var.get('path') is not None:
                variable.category_code = path_converter(blueprint_var.get('path'))

            if blueprint_var.get('label') is not None:
                variable.data_label = blueprint_var.get('label')

            if blueprint_var.get('word_map'):
                variable.word_map_dict = blueprint_var.get('word_map')

            if blueprint_var.get('concept_code'):
                variable.concept_code = blueprint_var.get('concept_code')

            if blueprint_var.get('force_categorical') and blueprint_var.get('data_type'):
                msg = "Both 'force_categorical' and 'data_type' found for {!r}".format(variable.header)
                raise BlueprintException(msg)

            elif blueprint_var.get('data_type'):
                variable.column_type = blueprint_var.get('data_type')

            elif blueprint_var.get('force_categorical'):
                variable.forced_categorical = blueprint_var.get('force_categorical') == "Y"

            reference_column = blueprint_var.get('reference_column')
            if reference_column is not None:
                try:
                    variable.reference_column = variable.datafile.df.columns.get_loc(reference_column) + 1
                except KeyError:
                    msg = 'Cannot find reference column {!r} within dataframe header'.format(reference_column)
                    raise BlueprintException(msg)

            expected_numerical = blueprint_var.get('expected_numerical')
            if expected_numerical and variable.is_numeric_in_datafile:
                min_expected = expected_numerical.get('min', '')
                try:
                    min_const = float(min_expected if min_expected != '' else '-Inf')
                except ValueError:
                    self.msgs.warning("Expected numerical for min constraint ({}), got {!r}."
                                      .format(variable.header, min_expected))

                max_expected = expected_numerical.get('max', '')
                try:
                    max_const = float(max_expected if max_expected != '' else 'Inf')
                except ValueError:
                    self.msgs.warning("Expected numerical for max constraint ({}), got {!r}."
                                      .format(variable.header, max_expected))

                if min_const > variable.min or max_const < variable.max:
                    self.msgs.warning("Value constraints exceeded for {}: {} to {}, where datafile has min:{}, max:{}".
                                      format(variable.header, min_const, max_const, variable.min, variable.max)
                                      )

            expected_categorical = blueprint_var.get('expected_categorical')
            if expected_categorical:
                unexpected = set(variable.unique_values) - set(expected_categorical)
                if unexpected:
                    self.msgs.warning("Unexpected values for {}. Expected: {}. Also found: {}".
                                      format(variable.header, expected_categorical, list(unexpected))
                                      )

    def add_datafile(self, filename, dataframe=None):
        """
        Add a clinical data file to study.

        :param filename: path to file or filename of file in clinical directory.
        :param dataframe: if given, add `pd.DataFrame` to study.
        """

        if isinstance(dataframe, pd.DataFrame):
            datafile = DataFile()
            datafile.df = dataframe

        else:
            if os.path.exists(filename):
                file_path = filename
            else:
                file_path = os.path.join(self.params.dirname, filename)
            assert os.path.exists(file_path), PathError(file_path)
            datafile = DataFile(file_path)

            # Check if file is in de clinical directory
            if not os.path.dirname(os.path.abspath(filename)) == self.params.dirname:
                datafile.df  # Force load df

        datafile.path = os.path.join(self.params.dirname, os.path.basename(filename))

        while self.get_datafile(datafile.name):
            new_name = input("Filename {!r} already taken, try again.  ".format(datafile.name))
            datafile.name = new_name if not new_name == '' else datafile.name

        safe_name = clean_for_namespace(datafile.name)
        self.__dict__[safe_name] = datafile

        if datafile.name not in self.ColumnMapping.included_datafiles:
            self.msgs.okay('Adding {!r} as clinical datafile to study.'.format(datafile.name))
            self.ColumnMapping.append_from_datafile(datafile)

    def get_variable(self, var_id: tuple):
        """
        Return a Variable object based on variable id.

        :param var_id: tuple of filename and column number.
        :return: `tmtk.Variable`.
        """
        df_name, column = var_id
        datafile = self.get_datafile(df_name)
        return Variable(datafile, column, self)

    def find_variables_by_label(self, label: str, in_file: str=None) -> list:
        """
        Search for variables based on data label. All labels are converted to lower case.

        :param label:
        :param in_file:
        :return:
        """
        sliced = self.ColumnMapping.df.iloc[:, 3] == label
        if in_file:
            sliced = sliced & (self.ColumnMapping.df.iloc[:, 0] == in_file)
        return [self.get_variable(x[0]) for x in self.ColumnMapping.df[sliced].iterrows()]

    def get_patients(self):
        """
        Creates a dictionary that has subject identifiers as keys and each value is a map
        that contains an nothing or an 'age' and/or 'gender' key that maps to this value.

        :return: patients dict.
        """

        def add_patient_properties(subjects_dict, destination, labels):
            vars_ = [v for label in labels for v in self.find_variables_by_label(label)]

            if len(vars_) > 1:
                print("More than one {!r} defined, will pick last "
                      "value found for each subject.".format(destination))

            for var in vars_:
                for k, v in zip(var.subj_id.values, var.values):
                    if v in (None, '', pd.np.nan):
                        continue

                    subjects_dict[k].update({destination: v})

        subj_id_vars = self.find_variables_by_label('SUBJ_ID')

        # Create dictionary where every subject is a key with value as empty dictionary
        subjects = {subj_id: {} for var in subj_id_vars for subj_id in var.values}

        add_patient_properties(subjects, 'gender', ('gender', 'Gender', 'GENDER', 'sex', 'Sex', 'SEX'))
        add_patient_properties(subjects, 'age', ('Age', 'age', 'AGE'))

        return subjects

    def get_trial_visits(self):
        """
        Returns a list of all trial visits present in this study. Visits are identified
        by the TRIAL_VISIT_LABEL keyword in column mapping and can be annotated with
        a value and unit using the TrialVisits object.

        :return: list of dicts.
        """

        visit_labels = {'General': {'name': 'General'}}
        visit_labels.update({l: {'name': l}
                             for var in self.find_variables_by_label('TRIAL_VISIT_LABEL')
                             for l in var.values})
        visit_labels.update({l: {'name': l} for l in self.TrialVisits.df.iloc[:, 0]})

        self.TrialVisits.df.apply(
            lambda x: visit_labels[x[0]].update(
                {'relative_time': x[1],
                 'time_unit': x[2]}
            ), axis=1
        )
        for missing in ('', None, pd.np.nan):
            try:
                visit_labels.pop(missing)
            except KeyError:
                pass

        return list(visit_labels.values())

    @property
    def all_variables(self):
        """
        Dictionary where {`tmtk.VarID`: `tmtk.Variable`} for all variables in
        the column mapping file.
        """
        return {VarID(var_id): self.get_variable(var_id) for var_id in self.ColumnMapping.ids}

    @property
    def filtered_variables(self):
        """
        Dictionary where {`tmtk.VarID`: `tmtk.Variable`} for all variables in
        the column mapping file that do not have a data label in the RESERVED_KEYWORDS list
        """
        return {k: v for k, v in self.all_variables.items()
                if v.data_label not in self.ColumnMapping.RESERVED_KEYWORDS}

    def validate_all(self, verbosity=3):
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'validate'):
                obj.validate(verbosity=verbosity)

    def get_datafile(self, name: str):
        """
        Find datafile object by filename.

        :param name: name of file.
        :return: `tmtk.DataFile` object.
        """
        for key, obj in self.__dict__.items():
            if isinstance(obj, DataFile):
                if obj.name == name:
                    return obj

    def __hash__(self):
        """
        Calculate hash for in memory pd.DataFrame objects.  The sum of these hashes
        is returned.

        :return: sum of hashes.
        """
        hashes = 0
        for key, obj in self.__dict__.items():
            if hasattr(obj, 'df'):
                hashes += hash(obj)
        return hashes

    def show_changes(self):
        """Print changes made to the column mapping and word mapping file."""
        column_changes = self.ColumnMapping.path_changes(silent=True)
        word_map_changes = self.WordMapping.word_map_changes(silent=True)

        changes = set().union(column_changes, word_map_changes)

        for var_id in changes:
            print("{}: {}".format(*var_id))
            path_change = column_changes.get(var_id)
            if path_change:
                print("       {}".format(path_change[0]))
                print("    -> {}".format(path_change[1]))
            else:
                print("       {}".format(self.get_variable(var_id).concept_path))

            map_change = word_map_changes.get(var_id)
            if map_change:
                for k, v in map_change.items():
                    print("          - {!r} -> {!r}".format(k, v))

        return changes

    @property
    def load_to(self):
        return TransmartBatch(param=self.params.path,
                              items_expected=self._get_lazy_batch_items()
                              ).get_loading_namespace()

    def _get_lazy_batch_items(self):
        return {self.params.path: [self.get_datafile(f).path for f in self.ColumnMapping.included_datafiles]}

    @property
    def clinical_files(self):
        return [x for k, x in self.__dict__.items() if issubclass(type(x), FileBase)]

    def _validate_clinical_params(self):
        if os.path.exists(self.params.path):
            self.msgs.okay('Clinical params found on disk.')
        else:
            self.msgs.error('Clinical params not on disk.')

    def _validate_SUBJ_IDs(self):
        for datafile in self.ColumnMapping.included_datafiles:
            var_id_list = [var_id for var_id in self.ColumnMapping.subj_id_columns if var_id[0] == datafile]

            # Check for one SUBJ_ID per file
            if len(var_id_list) == 1:

                subj_id = self.get_variable(var_id_list[0])
                if len(subj_id.values) == len(subj_id.unique_values):
                    self.msgs.okay('Found a SUBJ_ID for {} and it has unique values, thats good!'.format(datafile))
                else:
                    self.msgs.error('Found a SUBJ_ID for {}, but it has duplicate values.'.format(datafile),
                                    warning_list=subj_id.values[subj_id.values.duplicated()].unique())

            else:
                self.msgs.error('Found {} SUBJ_ID for {}'.format(len(var_id_list), datafile))

    def _validate_word_mappings(self):

        # check presence of all data files
        filenames = self.WordMapping.included_datafiles
        valid_filenames = []
        for filename in filenames:
            if filename not in self.ColumnMapping.included_datafiles:
                msg = "The file {} isn't included in the column map".format(filename)
                self.msgs.error(msg)
            else:
                valid_filenames.append(filename)
        
        column_number = self.WordMapping.df.columns[1]

        for filename in valid_filenames:
            datafile = self.get_datafile(filename)
            amount_of_columns = datafile.df.shape[1]

            columns = set(self.WordMapping.df.loc[filename, column_number])

            out_of_bound = {index for index in columns if index > amount_of_columns}
            for index in out_of_bound:
                msg = "File {} doesn't has {} columns, but {} columns".format(filename, index, amount_of_columns)
                self.msgs.error(msg)

            correct_columns = columns - out_of_bound
            for column in correct_columns:
                variable = self.get_variable((filename, column))
                unmapped = variable.word_mapped_not_present()
                for unmapped_value in unmapped:
                    msg = "Value {} is mapped at column {} in file {}. " \
                          "However the value is not present in the column".format(unmapped_value, column, filename)
                    self.msgs.warning(msg)
