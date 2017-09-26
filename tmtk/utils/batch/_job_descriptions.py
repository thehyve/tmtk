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
            pass
        else:
            return self.steps.get(step)

    @property
    def n_steps(self):
        return len(self.steps)


class ClinicalJob(JobStepsDescription):
    progress_bar_step = 'rowProcessingStep'
    step_list = [
        ('readWordMap', 'reading data files..'),
        ('readVariables', 'reading data files..'),
        ('readXtrialsFile', 'reading data files..'),
        ('gatherCurrentPatients', 'gathering patients..'),
        ('GatherCurrentConcepts', 'gathering concepts..'),
        ('gatherXtrialNodes', 'gathering cross trial nodes..'),
        ('deleteObservationFact', 'removing stuff, this takes a while..'),
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
        ('readMappingFile', 'reading subject mapping..'),
        ('failIfPlatformNotFound', 'checking platform..'),
        ('checkPlatformNotFound', 'checking platform..'),
        ('gatherCurrentConcepts', 'getting current concepts..'),
        ('validateTopNodePreexistence', 'getting current concepts..'),
        ('validateHighDimensionalConcepts', 'getting current concepts..'),
        ('gatherCurrentPatients', 'getting current patients..'),
        ('validatePatientIntersection', 'getting current patients..'),
        ('loadAnnotationMappings', 'loading annotation map..'),
        ('firstPass', 'checking a bunch of stuff, this takes a while..'),
        ('deleteHdData', 'removing stuff, this takes a while..'),
        ('deleteCurrentAssays', 'cleaning up prior to load..'),
        ('deleteConceptCounts', 'cleaning up prior to load..'),
        ('deleteObservationFact', 'cleaning up prior to load..'),
        ('insertConcepts', 'preparing load step..'),
        ('writePseudoFactsStep', 'preparing load step..'),
        ('insertConceptCounts', 'preparing load step..'),
        ('writeAssays', 'preparing load step..'),
        ('partitionDataTable', 'preparing load step..'),
        ('secondPass', 'loading data items..'),
    ]


class ChromosomalRegionJob(JobStepsDescription):
    progress_bar_step = 'insertChromosomalRegions'
    step_list = [
        ('deleteChromosomalRegions', 'deleting old stuff..'),
        ('deleteGplInfo', 'deleting old stuff..'),
        ('insertGplInfo', 'preparing for loading..'),
        ('insertChromosomalRegions', 'preparing for loading..'),
    ]


class ExpressionAnnotationJob(JobStepsDescription):
    progress_bar_step = 'mainStep'
    step_list = [
        ('deleteAnnotations', 'deleting old stuff..'),
        ('deleteGplInfo', 'deleting old stuff..'),
        ('insertGplInfo', 'preparing for loading..'),
        ('mainStep', 'preparing for loading..'),
    ]


class ProteomicsAnnotationJob(JobStepsDescription):
    progress_bar_step = 'mainStep'
    step_list = [
        ('deleteAnnotations', 'deleting old stuff..'),
        ('deleteGplInfo', 'deleting old stuff..'),
        ('insertGplInfo', 'preparing for loading..'),
        ('fillUniprotIdToUniprotNameMapping', 'setting identifiers..'),
        ('mainStep', 'preparing for loading..'),
    ]


class TagsJob(JobStepsDescription):
    progress_bar_step = 'tagsLoadStep'
    step_list = [
        ('GatherCurrentConcepts', 'getting current concepts..'),
        ('ValidateTopNodePreexistence', 'getting current concepts..'),
        ('tagsLoadStep', 'loading tags..'),
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
