from .skinny_loader.i2b2demodata.patient_mapping import PatientMapping
from .skinny_loader.i2b2demodata.study_table import StudyTable
from .skinny_loader.i2b2metadata.i2b2_secure import I2B2Secure
from .skinny_loader.i2b2demodata.concept_dimension import ConceptDimension
from .skinny_loader.i2b2demodata.modifier_dimension import ModifierDimension
from .skinny_loader.i2b2demodata.observation_fact import ObservationFact
from .skinny_loader.i2b2demodata.patient_dimension import PatientDimension
from .skinny_loader.i2b2demodata.trial_visit_dimension import TrialVisitDimension
from .skinny_loader.i2b2metadata.dimension_descriptions import DimensionDescription
from .skinny_loader.i2b2metadata.study_dimension_descriptions import StudyDimensionDescription

import os


class SkinnyExport:

    def __init__(self, study, export_directory=None):
        self.study = study
        self.export_directory = export_directory
        self.i2b2_secure = self._build_i2b2_secure()
        self.concept_dimension = self._build_concept_dimension()
        self.patient_dimension = self._build_patient_dimension()
        self.patient_mapping = self._build_patient_mapping()
        self.study_table = self._build_study_table()
        self.trial_visit_dimension = self._build_trial_visit_dimension()
        self.modifier_dimension = self._build_modifier_dimension()
        self.dimension_description = self._build_dimension_description()
        self.study_dimension_descriptions = self._build_study_dimension_descriptions()

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

    def build_observation_fact(self):
        self.observation_fact = ObservationFact(self)

    def observation_fact_to_disk(self):
        dir_path = os.path.join(self.export_directory, 'i2b2demodata')
        os.makedirs(dir_path, exist_ok=True)

        ObservationFact(self, straight_to_disk=os.path.join(dir_path, 'observation_fact.tsv'))
