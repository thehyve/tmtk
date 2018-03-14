from tests.commons import TestBase, create_study_from_dir
from tmtk import options
from tmtk.options import register_option, is_str


class OptionsTests(TestBase):

    @classmethod
    def setup_class_hook(cls):
        cls.study = create_study_from_dir('incomplete')

    def test_invalid_input(self):

        with self.assertRaises(ValueError):
            options.transmart_batch_mode = 1

        with self.assertRaises(ValueError):
            options.arborist_url = True

    def test_invalid_registration(self):
        with self.assertRaises(ValueError):
            register_option('no_good',
                            default=True,
                            validator=is_str)

    def test_callback(self):

        class Counter:
            def __init__(self):
                self.value = 0

            def __call__(self, *args, **kwargs):
                self.value += 1
                return self.value
        counter = Counter()

        register_option('counter',
                        default=True,
                        callback=counter)
        self.assertEqual(0, counter.value)
        options.counter = False
        self.assertEqual(1, counter.value)
        options.counter = False
        self.assertEqual(2, counter.value)

    def test_transmart_batch_mode_clinical_params(self):
        params_ = ('MODIFIERS_FILE', 'TRIAL_VISITS_FILE', 'ONTOLOGY_MAP_FILE')
        default = options.transmart_batch_mode

        try:
            options.transmart_batch_mode = True
            limited_study = create_study_from_dir('incomplete')
            for p in params_:
                self.assertTrue(hasattr(self.study.Clinical.params, p))
                self.assertFalse(hasattr(limited_study.Clinical.params, p))

            self.assertTrue(limited_study.Clinical.validate())
            limited_study = limited_study.write_to(self.temp_dir)

        finally:
            options.transmart_batch_mode = default
