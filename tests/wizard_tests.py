from unittest.mock import patch

import os

import tmtk
from tests.commons import TestBase

valid_inputs = ['0', '1', '']


def get_valid_input(*args, **kwargs):
    return valid_inputs.pop(0)


class WizardTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.wizard_dir = os.path.join(cls.studies_dir, 'wizard')

    @patch('tmtk.toolbox.wizard.get_input', side_effect=get_valid_input)
    def test_run_wizard(self, x):
        study = tmtk.toolbox.wizard.create_study(self.wizard_dir)
        self.assertEqual(2, len(study.Clinical.ColumnMapping.included_datafiles))