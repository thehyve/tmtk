from .AnnotationBase import AnnotationBase


class ChromosomalRegions(AnnotationBase):
    """
    Subclass for CNV (aCGh, qDNAseq) annotation
    """

    @property
    def biomarkers(self):
        return self.df.ix[:, 1]
