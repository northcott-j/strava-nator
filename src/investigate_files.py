import json
from src.file_utils import get_exercise_files


def investigate(file_path: str):
    """
    Checks data for validity and how much will be imported

    :param file_path: path to zip
    """
    _check_lat_long(file_path)


def _check_lat_long(file_path: str):
    """
    Checks to see if any files contains lat/long

    :param file_path: path to zip
    """
    count = 0
    for json_files in get_exercise_files(file_path).values():
        for json_file in json_files:
            try:
                with open(json_file, 'r') as infile:
                    data = json.load(infile)
                    for d in data:
                        if 'latitude' in d or 'longitude' in d:
                            count += 1
                            break
            except:
                print(f'Failed to parse {json_file}')
    if not count:
        raise Exception('No files have lat/long info')
    else:
        print(f'Found {count} files with location data!')
