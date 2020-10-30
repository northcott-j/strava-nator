import json
import glob
import datetime
from pathlib import Path
from base64 import b64encode
from collections import defaultdict
from typing import Set, Optional, Any, List, Dict
from src.exercise_manifest import build_manifest
from src.file_utils import get_exercise_files, setup_gpx_folders, save_gpx


def generate_gpx_files(file_path: str):
    """
    Create a directory with subfolders for exercise types with GPX files

    :param file_path: path to zip file
    """
    # NOTE :: Not going to generate files for unknown exercise types
    manifest = build_manifest(file_path, skip_unknown=True)
    all_exercise_files = get_exercise_files(file_path, exclude_internal=True)
    setup_gpx_folders(file_path, manifest.keys())
    for exercise_type, exercise_ids in manifest.items():
        exercise_count = 1
        for exercise_id in sorted(exercise_ids):
            exercise_files = all_exercise_files.get(exercise_id)
            exercise_name = f'{exercise_type.capitalize()} #{exercise_count} (Strava-nator)'
            gpx = _make_gpx(exercise_type, exercise_files, exercise_name)
            if gpx:
                exercise_id = f'{exercise_id}---{b64encode(exercise_name.encode("utf-8")).decode()}'
                save_gpx(file_path, exercise_type, exercise_id, gpx)
                exercise_count += 1


def _make_gpx(exercise_type: str, files: Set[str], exercise_name: str) -> Optional[str]:
    """
    Make a merged GPX file if location data is available.
    Naming convention is f'{exercise_type} #{count} (Strava-nator)'

    :param exercise_type: the type of exercise
    :param files: list of files to open and get exercise info
    :param exercise_name: name of this exercise
    :return: gpx content if location data is present
    """
    merged_data = _merge_data(files)
    if not merged_data: return None
    date_string = datetime.datetime.fromtimestamp(merged_data[0]['start_time']).isoformat()
    header = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<gpx creator="StravaGPX" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">'
        f'<metadata>'
        f'<time>{date_string}</time>'
        f'</metadata>'
        f'<trk>'
        f'<name>{exercise_name}</name>'
        f'<type>1</type>'
        f'<trkseg>'
    )
    body = []
    for d in merged_data:
        latitude = d.get('latitude')
        longitude = d.get('longitude')
        altitude = d.get('altitude')
        heart_rate = d.get('heart_rate')
        cadence = d.get('cadence')
        start_time = datetime.datetime.fromtimestamp(d['start_time']).isoformat()
        if latitude and longitude:
            body.append(f'<trkpt lat="{latitude}" lon="{longitude}">')
            body.append(f'<time>{start_time}</time>')
            if altitude: body.append(f'<ele>{altitude}</ele>')
            if cadence:
                cadence_gpx = (
                    f'<extensions>'
                    f'<cadence>{cadence}</cadence>'
                    f'</extensions>'
                )
                body.append(cadence_gpx)
            if heart_rate:
                hr_gpx = (
                    f'<extensions>'
                    f'<gpxtpx:TrackPointExtension>'
                    f'<gpxtpx:hr>{heart_rate}</gpxtpx:hr>'
                    f'</gpxtpx:TrackPointExtension>'
                    f'</extensions>'
                )
                body.append(hr_gpx)
            body.append('</trkpt>')
    closing = (
        f'</trkseg>'
        f'</trk>'
        f'</gpx>'
    )
    if len(body) == 0: return None
    print(f'Finished building {exercise_name}')
    body = "\n".join(body)
    return f'{header}{body}{closing}'


def _merge_data(files: Set[str]) -> Optional[List[Dict[str, Any]]]:
    """
    Merges info from all of the files together

    :param files: json files for this exercise
    """
    found_location_data = False
    merged_data = defaultdict(dict)
    for f in files:
        with open(f, 'r') as infile:
            data = json.load(infile)
            if not isinstance(data, List): break
            for d in data:
                if 'latitude' in d or 'longitude' in d: found_location_data = True
                if 'start_time' in d:
                    d['start_time'] = d['start_time'] / 1000
                    index_time = round(d['start_time'])
                    merged_data[index_time].update(d)
    return None if not found_location_data else list(sorted(merged_data.values(), key=lambda d: d['start_time']))
