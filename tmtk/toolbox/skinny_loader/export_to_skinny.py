from .i2b2demodata.patient_mapping import PatientMapping
from .i2b2demodata.study_table import StudyTable
from .i2b2metadata.i2b2_secure import I2B2Secure
from .i2b2demodata.concept_dimension import ConceptDimension
from .i2b2demodata.modifier_dimension import ModifierDimension
from .i2b2demodata.observation_fact import ObservationFact
from .i2b2demodata.patient_dimension import PatientDimension
from .i2b2demodata.trial_visit_dimension import TrialVisitDimension
from .i2b2metadata.dimension_descriptions import DimensionDescription
from .i2b2metadata.study_dimension_descriptions import StudyDimensionDescription

import os


class SkinnyExport:
    """
    This object creates pd.Dataframes that resemble tranSMART data base tables
    by transforming the tmtk.Study object. The goal is to create files that can
    be used by the skinny loader, which aims to do as little transformations as
    possible.
    """

    def __init__(self, study, export_directory=None):
        self.study = study
        self.export_directory = export_directory

        # Start by creating the tree in i2b2_secure
        self.i2b2_secure = self._build_i2b2_secure()
        # Nodes from concept dimension are added to i2b2_secure
        self.concept_dimension = self._build_concept_dimension()
        # We have to go back to add all missing folders
        self.i2b2_secure.add_missing_folders()

        self.patient_dimension = self._build_patient_dimension()
        self.patient_mapping = self._build_patient_mapping()
        self.study_table = self._build_study_table()
        self.trial_visit_dimension = self._build_trial_visit_dimension()
        if study.Clinical.Modifiers:
            self.modifier_dimension = self._build_modifier_dimension()
        self.dimension_description = self._build_dimension_description()
        self.study_dimension_descriptions = self._build_study_dimension_descriptions()

        # Observation fact has to be created explicitly, because it is the only expensive operation
        self.observation_fact = None

    def _build_i2b2_secure(self):
        return I2B2Secure(self.study)

    def _build_concept_dimension(self):
        return ConceptDimension(self.study, self.i2b2_secure)

    def _build_patient_dimension(self):
        return PatientDimension(self.study)

    def _build_patient_mapping(self):
        return PatientMapping(self.patient_dimension)

    def _build_study_table(self):
        return StudyTable(self.study)

    def _build_trial_visit_dimension(self):
        return TrialVisitDimension(self.study)

    def _build_modifier_dimension(self):
        return ModifierDimension(self.study)

    def _build_dimension_description(self):
        return DimensionDescription(self.study)

    def _build_study_dimension_descriptions(self):
        return StudyDimensionDescription(self.dimension_description)

    def to_disk(self):

        DEMO = 'i2b2demodata'
        META = 'i2b2metadata'

        attribute_to_disk_map = {
                             'i2b2_secure': (META, 'i2b2_secure.tsv'),
                       'concept_dimension': (DEMO, 'concept_dimension.tsv'),
                       'patient_dimension': (DEMO, 'patient_dimension.tsv'),
                         'patient_mapping': (DEMO, 'patient_mapping.tsv'),
                             'study_table': (DEMO, 'study.tsv'),
                   'trial_visit_dimension': (DEMO, 'trial_visit_dimension.tsv'),
                      'modifier_dimension': (DEMO, 'modifier_dimension.tsv'),
                   'dimension_description': (META, 'dimension_description.tsv'),
            'study_dimension_descriptions': (META, 'study_dimension_descriptions.tsv')
        }
        self._ensure_dirs()
        for attribute, file_tuple in attribute_to_disk_map.items():

            table_obj = getattr(self, attribute)

            if not table_obj:
                continue
            path = os.path.join(self.export_directory, file_tuple[0], file_tuple[1])
            with open(path, 'w') as f:
                print('Writing table to disk: {}'.format(path))
                table_obj.df.to_csv(f, sep='\t', index=False)

        self.observation_fact_to_disk()

    def build_observation_fact(self):
        self.observation_fact = ObservationFact(self)

    def observation_fact_to_disk(self):
        self._ensure_dirs()
        path = os.path.join(self.export_directory, 'i2b2demodata', 'observation_fact.tsv')
        print('Writing table to disk: {}'.format(path))
        ObservationFact(self, straight_to_disk=path)

    def _ensure_dirs(self):
        if self.export_directory:
            for dir_ in ('i2b2demodata', 'i2b2metadata'):
                os.makedirs(os.path.join(self.export_directory, dir_), exist_ok=True)
        else:
            raise Exception('Need to set export_directory.')