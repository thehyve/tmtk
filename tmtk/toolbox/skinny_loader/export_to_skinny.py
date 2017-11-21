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
from .i2b2metadata.i2b2_tags import I2B2Tags

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

        # Start by creating the concept_dimension
        self.concept_dimension = ConceptDimension(self.study)

        # Nodes from concept dimension
        self.i2b2_secure = I2B2Secure(self.study, self.concept_dimension)

        # First we build the patient_dimension and then the patient mapping based on that
        self.patient_dimension = PatientDimension(self.study)
        self.patient_mapping = PatientMapping(self.patient_dimension)

        if study.Clinical.Modifiers:
            self.modifier_dimension = ModifierDimension(self.study)
        if hasattr(study, 'Tags'):
            self.i2b2_tags = I2B2Tags(self.study)

        # Some small study descriptions
        self.study_table = StudyTable(self.study)
        self.trial_visit_dimension = TrialVisitDimension(self.study)
        self.dimension_description = DimensionDescription(self.study)
        self.study_dimension_descriptions = StudyDimensionDescription(self.dimension_description)

        # Observation fact has to be created explicitly, because it is the only expensive operation
        self.observation_fact = None

    def to_disk(self):

        demo = 'i2b2demodata'
        meta = 'i2b2metadata'

        attribute_to_disk_map = {
            'i2b2_secure': (meta, 'i2b2_secure.tsv'),
            'i2b2_tags': (meta, 'i2b2_tags.tsv'),
            'concept_dimension': (demo, 'concept_dimension.tsv'),
            'patient_dimension': (demo, 'patient_dimension.tsv'),
            'patient_mapping': (demo, 'patient_mapping.tsv'),
            'study_table': (demo, 'study.tsv'),
            'trial_visit_dimension': (demo, 'trial_visit_dimension.tsv'),
            'modifier_dimension': (demo, 'modifier_dimension.tsv'),
            'dimension_description': (meta, 'dimension_description.tsv'),
            'study_dimension_descriptions': (meta, 'study_dimension_descriptions.tsv')
        }
        self._ensure_dirs()
        for attribute, file_tuple in attribute_to_disk_map.items():

            table_obj = getattr(self, attribute, 0)

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