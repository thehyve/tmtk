from .ParamsBase import ParamsBase
import os


class AnnotationParams(ParamsBase):
    @property
    def mandatory(self):
        return {'PLATFORM': {
            'helptext': 'Short identifier for platform.'
        },
            'TITLE': {
                'helptext': 'Platform description.'
            },
            'ANNOTATIONS_FILE': {
                'variable_type': 'filename',
                'helptext': 'Points to the annotations file.'
            }
        }

    @property
    def optional(self):
        return {'ORGANISM': {
            'helptext': 'Usually Homo sapiens.'
        },
            'GENOME_RELEASE': {
                'helptext': 'Something like hg19 or hg38.  Only required when'
                            ' genomic coordinates are provided in the file.'
            },
        }

    def is_viable(self):
        """

        :return: True if both the platform is set and the annotations file is located,
            else returns False.
        """
        if self.get('ANNOTATIONS_FILE') and self.get('PLATFORM'):
            file_found = os.path.exists(os.path.join(self.dirname, self.ANNOTATIONS_FILE))
            return file_found
        else:
            return False
