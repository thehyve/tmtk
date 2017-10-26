from .skinny_loader.i2b2_secure import I2B2Secure
from .skinny_loader.concept_dimension import ConceptDimension
from .skinny_loader.patient_dimension import PatientDimension
from .skinny_loader.patient_mapping import PatientMapping
from .skinny_loader.study_table import StudyTable
from .skinny_loader.trial_visit_dimension import TrialVisitDimension
from .skinny_loader.observation_fact import ObservationFact


class SkinnyExport:

    def __init__(self, study):
        self.study = study
        self.i2b2_secure = self._build_i2b2_secure()
        self.concept_dimension = self._build_concept_dimension()
        self.patient_dimension = self._build_patient_dimension()
        self.patient_mapping = self._build_patient_mapping()
        self.study_table = self._build_study_table()
        self.trial_visit_dimension = self._build_trial_visit_dimension()
        self.observation_fact = self._build_observation_fact()

    def _build_i2b2_secure(self):
        return I2B2Secure(self.study)

    def _build_concept_dimension(self):
        return ConceptDimension(self.study)

    def _build_patient_dimension(self):
        return PatientDimension(self.study)

    def _build_patient_mapping(self):
        return PatientMapping(self.patient_dimension)

    def _build_study_table(self):
        return StudyTable(self.study)

    def _build_trial_visit_dimension(self):
        return TrialVisitDimension(self.study)

    def study_dimension_descriptions(self):
        pass

    def modifier_dimension(self):
        pass

    def _build_observation_fact(self):
        return ObservationFact(self)
