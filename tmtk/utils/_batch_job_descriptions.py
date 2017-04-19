from collections import OrderedDict


class JobStepsDescription:

    def __init__(self):
        self.steps = OrderedDict()
        for step, description in self.step_list:
            self.add(step, description)

    def add(self, name, description):
        self.steps.update({name: description})

    def position_of(self, step):
        try:
            return list(self.steps.keys()).index(step) + 1
        except ValueError:
            pass

    def description_of(self, step):

        if not self.steps.get(step):
            print('Job description not found for: {}'.format(step))
        else:
            return self.steps.get(step)

    @property
    def n_steps(self):
        return len(self.steps)


class ClinicalJob(JobStepsDescription):
    progress_bar_step = 'rowProcessingStep'
    step_list = [
        ('readWordMap', 'reading wordmap..'),
        ('readVariables', 'reading variables..'),
        ('readXtrialsFile', 'reading cross trial file..'),
        ('gatherCurrentPatients', 'gathering patients..'),
        ('GatherCurrentConcepts', 'gathering concepts..'),
        ('gatherXtrialNodes', 'gathering cross trial nodes..'),
        ('deleteObservationFact', 'deleting observations, this could take a while..'),
        ('deleteConceptCounts', 'deleting concept counts..'),
        ('rowProcessingStep', 'loading data items..'),
        ('tagsLoadStep', 'loading metadata tags..'),
        ('CreateSecureStudy', 'setting security tags..'),
        ('InsertTableAccess', 'ensuring table access..'),
        ('insertConceptCountsStep', 'updating concept counts..'),
    ]


class HighDimJob(JobStepsDescription):
    progress_bar_step = 'secondPass'
    step_list = [
        ('readMappingFile', 'Description not set'),
        ('failIfPlatformNotFound', 'Description not set'),
        ('checkPlatformNotFound', 'Description not set'),
        ('gatherCurrentConcepts', 'Description not set'),
        ('validateTopNodePreexistence', 'Description not set'),
        ('validateHighDimensionalConcepts', 'Description not set'),
        ('gatherCurrentPatients', 'Description not set'),
        ('validatePatientIntersection', 'Description not set'),
        ('loadAnnotationMappings', 'Description not set'),
        ('firstPass', 'Description not set'),
        ('deleteHdData', 'Description not set'),
        ('deleteCurrentAssays', 'Description not set'),
        ('deleteConceptCounts', 'Description not set'),
        ('deleteObservationFact', 'Description not set'),
        ('insertConcepts', 'Description not set'),
        ('writePseudoFactsStep', 'Description not set'),
        ('insertConceptCounts', 'Description not set'),
        ('writeAssays', 'Description not set'),
        ('partitionDataTable', 'Description not set'),
        ('secondPass', 'Description not set'),
    ]


class ChromosomalRegionJob(JobStepsDescription):
    progress_bar_step = 'insertChromosomalRegions'
    step_list = [
        ('deleteChromosomalRegions', 'Description not set'),
        ('deleteGplInfo', 'Description not set'),
        ('insertGplInfo', 'Description not set'),
        ('insertChromosomalRegions', 'Description not set'),
    ]


class ExpressionAnnotationJob(JobStepsDescription):
    progress_bar_step = 'mainStep'
    step_list = [
        ('deleteAnnotations', 'Description not set'),
        ('deleteGplInfo', 'Description not set'),
        ('insertGplInfo', 'Description not set'),
        ('mainStep', 'Description not set'),
    ]


class ProteomicsAnnotationJob(JobStepsDescription):
    progress_bar_step = 'mainStep'
    step_list = [
        ('deleteAnnotations', 'Description not set'),
        ('deleteGplInfo', 'Description not set'),
        ('insertGplInfo', 'Description not set'),
        ('fillUniprotIdToUniprotNameMapping', 'Description not set'),
        ('mainStep', 'Description not set'),
    ]


class TagsJob(JobStepsDescription):
    progress_bar_step = 'tagsLoadStep'

    step_list = [
        ('GatherCurrentConcepts', 'Description not set'),
        ('ValidateTopNodePreexistence', 'Description not set'),
        ('tagsLoadStep', 'Description not set'),
        ]

job_map = {'clinical.params': ClinicalJob(),
           'cnv.params': HighDimJob(),
           'cnv_annotation.params': ChromosomalRegionJob(),
           'rnaseq.params': HighDimJob(),
           'rnaseq_annotation.params': ChromosomalRegionJob(),
           'expression.params': HighDimJob(),
           'mrna_annotation.params': ExpressionAnnotationJob(),
           'proteomics.params': HighDimJob(),
           'proteomics_annotation.params': ProteomicsAnnotationJob(),
           'mirna.params': HighDimJob(),
           'mirna_annotation.params': ExpressionAnnotationJob(),
           'tags.params': TagsJob(),
           }
