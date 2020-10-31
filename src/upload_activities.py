import sys
import time
import datetime
from threading import Thread
from stravalib import Client
from collections import defaultdict
from typing import Dict, Set, List, Tuple
from src.server.server import start
from src.constants import STRAVA_RATE_LIMIT, STRAVA_RATE_INTERVAL
from src.file_utils import get_upload_files, mark_uploaded, get_gpx_metadata


def upload_new_gpx(file_path: str):
    """
    Uploads any new GPX files that haven't been seen before

    :param file_path: the path to zip
    """
    c = Client()
    _start_oauth_server(c)
    time.sleep(5)
    _wait_for_oauth()
    _double_check_user(c)
    new_files = get_upload_files(file_path)
    _double_check_file_counts(new_files)
    _upload_files(_sort_rename_files(new_files), c, file_path)


def _start_oauth_server(client: Client):
    """
    Need to start a local Flask server in order to get creds to make API calls

    :param client: the client instance that will be authorized to make calls
    """
    t = Thread(target=start, args=(client,))
    t.daemon = True
    t.start()


def _wait_for_oauth():
    """
    Raw Input to wait for the user to complete the auth flow
    """
    print('Please go to {http://localhost:5000} that is printed and follow in the browser')
    input('Input your access token and hit Enter: ')


def _double_check_user(client: Client):
    """
    Make sure this is the right user

    :param client: client that should now be authorized
    """
    try:
        user = client.get_athlete()
    except:
        print('hmmm it seems we are not authorized to access your Strava...')
        sys.exit(1)
    print(f'Are you {user.firstname} {user.lastname}?')
    input('Hit ctrl-c if this is wrong otherwise hit enter...')


def _double_check_file_counts(new_files: Dict[str, Set[str]]):
    """
    Makes sure the right number of files are being uploaded

    :param new_files: new GPX files that have been found
    """
    for exercise, files in new_files.items():
        print(f'Found {len(files)} GPX files for activity:{exercise}')
    if len(new_files) == 0:
        print('No new files to upload for you...')
        sys.exit(0)
    input('Hit ctrl-c if this is wrong otherwise hit enter...')


def _sort_rename_files(new_files: Dict[str, Set[str]]) -> List[Tuple[str, Dict[str, str]]]:
    """
    Takes the dict of exercise -> files and will flatten and sort them
    It will also append number if there's an identical exercise in a day

    :param new_files: dict of new files
    :return: sorted array of (path, gpx_metadata)
    """
    files = set()
    for file_set in new_files.values():
        files.update(file_set)
    file_name_mapping = defaultdict(list)
    for f in files:
        metadata = get_gpx_metadata(f)
        file_name_mapping[metadata['exercise_name']].append((f, metadata))
    files = []
    for gpx_files in file_name_mapping.values():
        if len(gpx_files) > 1:
            gpx_files = sorted(gpx_files, key=lambda g: g[1]['start_time'])
            count = 1
            for path, metadata in gpx_files:
                metadata['exercise_name'] = metadata['exercise_name'].replace('(Strava-nator)', f'#{count} (Strava-nator)')
                count += 1
        files.extend(gpx_files)
    return list(sorted(files, key=lambda f: f[1]['start_time']))


def _upload_files(new_files: List[Tuple[str, Dict[str, str]]],
                  client: Client, file_path: str):
    """
    Upload these files to the Strava API

    :param new_files: list of tuples of (path, gpx_metadata)
    :param client: client instance that should now be authorized
    :param file_path: path to zip
    """
    requests_left = STRAVA_RATE_LIMIT
    interval_start_time = time.time()
    for path, data in new_files:
        if requests_left == 0:
            _wait_for_reset(interval_start_time)
            requests_left = STRAVA_RATE_LIMIT
            interval_start_time = time.time()
        elif _passed_reset_interval(interval_start_time):
            requests_left = STRAVA_RATE_LIMIT
            interval_start_time = time.time()
        f_id = data['exercise_id']
        f_name = data['exercise_name']
        exercise = data['exercise_type']
        try:
            print(f'Uploading {f_name}...')
            with open(path, 'r') as infile:
                response = client.upload_activity(infile, 'gpx', name=f_name,
                                                  description="Uploaded Samsung Health activity using Strava-nator",
                                                  activity_type=exercise, external_id=f_id)
            while response.is_processing:
                time.sleep(5)
                response.poll()
                requests_left -= 1
            if response.is_error:
                print(f'Error: {response.error}')
                response.raise_for_error()
        except:
            print(f'...failed while uploading: {f_id} ({f_name})')
            continue
        mark_uploaded(file_path, f_id)
        requests_left -= 1



def _wait_for_reset(start_time: float):
    """
    Need to wait 15 minutes or have the 00, 15, 30, 45 time pass to reset rate limit

    :param start_time: the time when the last burst of requests was made
    """
    time_since = (time.time() - start_time).total_seconds / 60
    print('Ran out of requests. Need to wait 15 minutes or until an interval passes...')
    while time_since < STRAVA_RATE_INTERVAL and not _passed_reset_interval(start_time):
        time.sleep(10)
        time_since = (time.time() - start_time).total_seconds / 60


def _passed_reset_interval(start_time: float) -> bool:
    """
    Whether or not the time has gone past an interval point

    :param start_time: time when the last burst of requests started
    :return: True if interval has been passed
    """
    now = datetime.datetime.now()
    start = datetime.datetime.utcfromtimestamp(start_time)
    if now.hour != start.hour: return True
    intervals = set(range(0, 60, STRAVA_RATE_INTERVAL))
    minutes_since = set(range(max(start.minute, 1), now.minute))
    return len(intervals.intersection(minutes_since)) > 0
