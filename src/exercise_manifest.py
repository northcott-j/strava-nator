import csv
import glob
from pathlib import Path
from typing import Dict, Set
from collections import defaultdict
from src.file_utils import get_data_path
from src.constants import SAMSUNG_EXERCISE_MAPPINGS, SAMSUNG_EXERCISE_TYPE_HEADER, SAMSUNG_LOCATION_DATA_HEADER


def build_manifest(file_path: str, skip_unknown: bool = False) -> Dict[str, Set[str]]:
    """
    Uses the provided exercise CSV to get a manifest of exercises and their file_ids.

    :param file_path: path to zip file
    :param skip_unknown: whether or not to exclude known exercises
    :return: dict of exercise to a set of ids to identify relevant files
    """
    data_path = get_data_path(file_path)
    exercise_csv = _find_exercise_csv(data_path)
    manifest = _build_manifest(exercise_csv)
    if skip_unknown: manifest = {k: v for k, v in manifest.items() if 'unknown' not in k}
    return manifest


def _find_exercise_csv(data_path: str) -> str:
    """
    Find CSV enumerating the exercises

    :param data_path: path to relative data folder
    :return: path to the CSV
    """
    for path in glob.glob(str(Path(data_path) / '*.csv')):
        if '.exercise.' in path and 'pacesetter' not in path:
            return path
    raise Exception('Cannot locate file with all exercise info')


def _build_manifest(csv_path: str) -> Dict[str, Set[str]]:
    """
    Parses CSV and find exercises with location data

    :param csv_path: path to exercise csv
    :return: dict of exercise type to ids
    """
    exercises = defaultdict(set)
    # NOTE :: SHealth CSV has weird first row with some metadata
    skipped_metadata = False
    headers = None
    with open(csv_path, 'r') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if not skipped_metadata:
                skipped_metadata = True
            elif headers is None:
                headers = row
            else:
                row = {headers[i].lower(): row[i] for i in range(len(headers))}
                location_data = row.get(SAMSUNG_LOCATION_DATA_HEADER)
                exercise_type = row.get(SAMSUNG_EXERCISE_TYPE_HEADER)
                if location_data and exercise_type:
                    file_id = location_data.split('.')[0]
                    exercises[SAMSUNG_EXERCISE_MAPPINGS.get(exercise_type, f'unknown-{exercise_type}')].add(file_id)
    return exercises
