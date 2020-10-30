import os
import glob
from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict
from typing import Dict, Set, Iterable
from src.constants import STRAVANATOR_FOLDER


def prep_working_dir(file_path: str):
    """
    Uncompress the zip file in the data folder. Will not do it if it already
    exists. If the folder is nested, it'll flatten it.

    :param file_path: path to zipped dir
    """
    data_path = get_data_path(file_path)
    if not os.path.isfile(file_path):
        raise Exception(f'{file_path} does not exist!')
    if os.path.isdir(data_path):
        print('Folder already exists. skipping zip file processing...')
    else:
        _extract_zip_dir(file_path, data_path)

def get_data_path(file_path: str) -> str:
    """
    Creates a path for a dir of the right name in the relative data folder

    :param file_path: the path to the zip file
    :return: path to a dir in the data folder
    """
    file_path = file_path.replace('.zip', '')
    split_char = '/' if '/' in file_path else '\\'
    file_name = file_path.split(split_char)[-1]
    return Path(__file__).parent.parent / f"data/{file_name}"


def get_exercise_files(file_path: str, exclude_internal: bool = False) -> Dict[str, Set[str]]:
    """
    Gets all exercise JSON files

    :param file_path: path to zip file
    :param exclude_internal: don't include internal data files
    :return: dict of id -> set of file paths
    """
    files = defaultdict(set)
    data_path = get_data_path(file_path)
    json_path = Path(data_path) / "jsons"
    if not os.path.isdir(json_path):
        raise Exception('Cannot find any json files in extract')
    exercise_path = Path(json_path) / _get_exercise_path(json_path)
    for json_file in glob.glob(str(Path(exercise_path) / '**/*.json')):
        split_char = '/' if '/' in json_file else '\\'
        file_name = json_file.split(split_char)[-1]
        file_id = file_name.split('.')[0]
        if not (exclude_internal and 'internal' in json_file):
            files[file_id].add(json_file)
    return files


def setup_gpx_folders(file_path: str, exercises: Iterable[str]):
    """
    Generate folders to save GPX files

    :param file_path: path to zip
    :param exercises: exercises to make folders for
    """
    data_path = get_data_path(file_path)
    root_folder = Path(data_path) / STRAVANATOR_FOLDER
    if not os.path.isdir(root_folder): os.mkdir(root_folder)
    for e in exercises:
        e_path = root_folder / e
        if not os.path.isdir(e_path): os.mkdir(e_path)


def save_gpx(file_path: str, exercise_type: str, exercise_id: str, gpx: str):
    """
    Saves a GPX file for a particular exercise

    :param file_path: path to zip
    :param exercise_type: the type of exercise to save in correct subfolder
    :param exercise_id: id of exercise used for naming file
    :param gpx: gpx content
    """
    data_path = get_data_path(file_path)
    exercise_folder = Path(data_path) / STRAVANATOR_FOLDER / exercise_type
    exercise_file = exercise_folder / f'{exercise_id}.gpx'
    with open(exercise_file, 'w') as outfile:
        outfile.write(gpx)


def _extract_zip_dir(file_path: str, data_path: str):
    """
    Extracts directory from zipfile and saves it in data

    :param file_path: path to the zip file
    :param data_path: path of dir to extract it to
    """
    zip = ZipFile(file_path)
    prefix = _find_zip_prefix(zip)
    for info in zip.infolist():
        if info.filename[-1] != '/':
            info.filename = info.filename.replace(prefix, "")
            zip.extract(info, data_path)
    zip.close()


def _find_zip_prefix(zip: ZipFile) -> str:
    """
    Sees if the zip has a nested directory

    :param zip: the open zipfile
    :return: prefix to remove
    """
    for path in zip.namelist():
        split_char = '/' if '/' in path else '\\'
        # NOTE :: Assuming jsons folder exists and should be in root
        if f'jsons{split_char}' in path:
            prefix = path.split(split_char)[0]
            return '' if prefix == 'jsons' else f'{prefix}{split_char}'
    raise Exception('ZipFile is of an unknown structure...')


def _get_exercise_path(json_path: str) -> str:
    """
    Get path to folder with exercise jsons

    :param json_path: path to json files folder
    """
    for path in os.listdir(json_path):
        if path.endswith('.exercise'):
            return path
    raise Exception('Could not find a folder with JSON exercise files')
