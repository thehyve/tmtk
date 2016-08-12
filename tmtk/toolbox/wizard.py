import os as _os
import glob as _glob

from ..study import Study as _Study
from ..params import StudyParams as _StudyParams


def create_study(path):
    """
    Start a study object by pointing by giving a folder that contains clinical data files only.

    :param path: path to folder with files.
    :return: study object.
    """
    path = _base_dir(path)

    study_params_path = _os.path.join(path, 'study.params')
    study = _Study(study_params_path)
    study.Params.study = _StudyParams(study_params_path, subdir='study', parent=study)

    clinical_params = _clinical_param_or_none(study)
    if clinical_params:
        clinical_params.update()
    else:
        p = _os.path.join(path, 'clinical', 'clinical.params')
        study.Params.add_params(p)
        clinical_params = _clinical_param_or_none(study)
        study.add_clinical(clinical_params)

    file_list = study.Clinical.ColumnMapping.included_datafiles or []
    if _os.path.exists(_os.path.join(path, clinical_params.COLUMN_MAP_FILE)):
        print('Column mapping file found that includes {}. Are there any other clinical files?'.
              format(file_list))

    clinical_data_files = _select_files(path, "Please select your clinical datafiles")
    new_files = [f for f in clinical_data_files if _os.path.basename(f) not in file_list]

    for data_file in new_files:
        new_file_path = _os.path.join(clinical_params.dirname, _os.path.basename(data_file))
        study.Clinical.add_datafile(data_file)
        file_obj = study.Clinical.get_datafile(_os.path.basename(data_file))
        file_obj.path = new_file_path

    return study


def _base_dir(path):
    path = _os.path.abspath(path)

    if not _os.path.isdir(path):
        path = _os.path.basename(path)

    return path


def _clinical_param_or_none(study):
    """
    Return study clinical params if it exists, else returns None.

    :param study: study object
    :return: params object or None
    """
    clinical_params = study.find_params_for_datatype('clinical')
    return clinical_params[0] if clinical_params else None


def _select_files(path, text):
    files_in_dir = [f for f in _glob.iglob(_os.path.join(path, '**'), recursive=True)
                    if not _os.path.isdir(f)]
    selected_files = []

    print('#####  {}  #####'.format(text))

    for i, f in enumerate(files_in_dir):
        print('-    {}. {}'.format(i, f))

    while True:
        number = input('Pick number:  ')

        if not number:
            break

        try:
            choice = int(number)
            filename = files_in_dir[choice]
            selected_files.append(filename)
        except (ValueError, IndexError):
            pass
        print('Selected files: {}'.format([_os.path.basename(f) for f in set(selected_files)]))

    return selected_files
