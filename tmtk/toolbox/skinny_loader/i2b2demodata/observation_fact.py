from ..shared import TableRow, Defaults, get_full_path, get_unix_timestamp

import pandas as pd
import arrow
from tqdm import tqdm


class ObservationFact(TableRow):
    def __init__(self, skinny, straight_to_disk=False):

        self.skinny = skinny
        self.study = skinny.study
        self._now = arrow.now().isoformat(sep=' ')
        super().__init__()

        self.df = None
        self._subject_id_cache = {}

        if not straight_to_disk:
            self._build_in_memory()
        else:
            self.write_to_disk(straight_to_disk)

    def _build_in_memory(self):

        dfs = []
        # Loop through all variables in the clinical data and add a row
        for variable in tqdm(self.study.Clinical.filtered_variables.values()):
            dfs += [r for r in self.build_rows(variable)]

        self.df = pd.concat(dfs, ignore_index=True)

    def write_to_disk(self, path):
        with open(path, 'w') as f:
            f.write('\t'.join(self.columns) + '\n')
            for variable in tqdm(self.study.Clinical.filtered_variables.values()):
                for df in self.build_rows(variable):
                    df.to_csv(f, sep='\t', index=False, header=False)

    def build_rows(self, var) -> pd.DataFrame:
        """
        Returns all observation fact rows for a given variable as multiple pd.DataFrames.
        It returns a DataFrame for all normal observations and one for each applicable modifier.
        """

        def get_value_fields(values, visual_attributes_):
            """
            Update a row object with its value based on visual_attributes

            :param values: values series.
            :param visual_attributes_: visual attributes determine the type of variable (unfortunately).
            :return: dictionary with variable type appropriate mapping.
            """
            if visual_attributes_ == var.VIS_DATE:
                return {'valtype_cd': 'N',
                        'tval_char': 'E',
                        'nval_num': values.apply(get_unix_timestamp),  # Unix time
                        'observation_blob': values}  # UTC

            elif visual_attributes_ == var.VIS_TEXT:
                return {'valtype_cd': 'B',
                        'tval_char': pd.np.nan,
                        'nval_num': pd.np.nan,
                        'observation_blob': values}

            elif visual_attributes_ == var.VIS_NUMERIC:
                return {'valtype_cd': 'N',
                        'tval_char': 'E',
                        'nval_num': values,
                        'observation_blob': pd.np.nan}

            elif visual_attributes_ == var.VIS_CATEGORICAL:
                return {'valtype_cd': 'T',
                        'tval_char': values,
                        'nval_num': pd.np.nan,
                        'observation_blob': pd.np.nan}

        # Preload these, so we don't have to get them for every value in the current variable
        modifiers = var.modifiers
        start_date = var.start_date
        var_full_path = get_full_path(var, self.study)

        concept_code = var.concept_code or self.skinny.concept_dimension.map.get(var_full_path)

        if not concept_code:
            raise Exception('No concept code found for {}'.format(var))

        try:
            internal_subj_ids = self._subject_id_cache[var.filename]
        except KeyError:
            internal_subj_ids = var.subj_id.values.map(self.skinny.patient_mapping.map)
            self._subject_id_cache[var.filename] = internal_subj_ids

        var_wide_data = {
            'encounter_num': -1,
            # Find the internal identifiers for a given series of external identifiers
            'patient_num': internal_subj_ids,
            'concept_cd': var.concept_code or self.skinny.concept_dimension.map.get(var_full_path),
            'provider_id': '@',
            'start_date': start_date.values if start_date else None,
            'modifier_cd': '@',
            # trial visits other than default 'General' are currently not supported
            'trial_visit_num': self.skinny.trial_visit_dimension.map[Defaults.TRIAL_VISIT],
            'instance_num': 1}

        var_wide_data.update(
            get_value_fields(var.mapped_values, var.visual_attributes)
        )

        # This dataframe contains all normal values, but also rows for missing values.
        main_df = pd.DataFrame(var_wide_data, columns=self.columns)

        if not modifiers:
            # Keep only observations that respond are non pd.np.nan
            yield main_df.loc[var.mapped_values.notnull()]

        else:
            # We have to also return the rows for the applicable modifier
            # variables and cleanup of empty observations is a bit more complicated.
            # Container for DataFrames for the applicable modifier variables.
            modifier_dfs = []

            for modifier_variable in modifiers:
                var_wide_data['modifier_cd'] = modifier_variable.modifier_code

                var_wide_data.update(
                    get_value_fields(modifier_variable.mapped_values, modifier_variable.visual_attributes)
                )
                modifier_dfs.append(pd.DataFrame(var_wide_data, columns=self.columns))

            # To cleanup of 'empty' observations, we first remove observations that are empty
            # themselves and have no modifier exists with a value either. The rule here is that
            # if any observation exists for a given patient/concept (etc..) combination, we keep the
            # empty observation. Modifiers without value will always be dropped.
            observations_present = [mod.mapped_values.notnull() for mod in modifiers] + [var.mapped_values.notnull()]
            any_present = pd.DataFrame(observations_present).any()

            # subset on inverted boolean series
            yield main_df.loc[any_present]

            # Strip modifier DataFrames of empty observations
            for i, modifier_variable in enumerate(modifiers):
                mod_df = modifier_dfs[i]
                mod_value_present = observations_present[i]
                # subset inverted boolean series
                yield mod_df.loc[mod_value_present]

    @property
    def _row_definition(self):
        return pd.Series(
            data=[
                -1,    # encounter_num
                None,  # patient_num
                None,  # concept_cd
                '@',   # provider_id
                None,  # start_date
                '@',   # modifier_cd
                1,     # instance_num
                None,  # trial_visit_num
                None,  # valtype_cd
                None,  # tval_char
                None,  # nval_num
                None,  # valueflag_cd
                None,  # quantity_num
                None,  # units_cd
                None,  # end_date
                None,  # location_cd
                None,  # observation_blob
                None,  # confidence_num
                None,  # update_date
                None,  # download_date
                None,  # import_date
                None,  # sourcesystem_cd
                None,  # upload_id
                None,  # sample_cd
            ],
            index=[
                'encounter_num',
                'patient_num',
                'concept_cd',
                'provider_id',
                'start_date',
                'modifier_cd',
                'instance_num',
                'trial_visit_num',
                'valtype_cd',
                'tval_char',
                'nval_num',
                'valueflag_cd',
                'quantity_num',
                'units_cd',
                'end_date',
                'location_cd',
                'observation_blob',
                'confidence_num',
                'update_date',
                'download_date',
                'import_date',
                'sourcesystem_cd',
                'upload_id',
                'sample_cd',
            ])
