from .skinny_loader.i2b2_secure import I2B2Secure
from .skinny_loader.concept_dimension import ConceptDimension


class SkinnyExport:

    def __init__(self, study):
        self.study = study
        self.i2b2_secure = self._build_i2b2_secure()
        self.concept_dimension = self._build_concept_dimension()

    def _build_i2b2_secure(self):
        return I2B2Secure(self.study)

    def _build_concept_dimension(self):
        return ConceptDimension(self.study)

    def study_dimension_descriptions(self):
        pass

    def modifier_dimension(self):
        pass

    def patient_dimension(self):
        pass

    def patient_mapping(self):
        pass

    def study(self):
        pass

    def trial_visit_dimension(self):
        pass

    def observation_fact(self):
        pass
