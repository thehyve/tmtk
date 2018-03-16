import tmtk
from .base import ParamsBase


class ClinicalParams(ParamsBase):
    docslink = "https://github.com/thehyve/transmart-batch/blob/master/docs/clinical.md"

    @property
    def mandatory(self):
        return {
            'COLUMN_MAP_FILE': {
                'mandatory': True,
                'helptext': 'Points to the column file.'
            }
        }

    @property
    def optional(self):
        params_ = {
            "WORD_MAP_FILE": {
                'helptext': 'Points to the file with dictionary to be used.'
            },
            "XTRIAL_FILE": {
                'helptext': 'Points to the cross study concepts file.'
            },
            "TAGS_FILE": {
                'helptext': 'Points to the concepts tags file.'
            }
        }
        if not tmtk.options.transmart_batch_mode:
            params_.update({
                "ONTOLOGY_MAP_FILE": {
                    'helptext': 'Points to the ontology mapping for this study.'
                },
                "MODIFIERS_FILE": {
                    'helptext': 'Points to the modifiers file for this study.'
                },
                "TRIAL_VISITS_FILE": {
                    'helptext': 'Points to the trial visits file for this study.'
                }
            })
        return params_
