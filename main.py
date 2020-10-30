import sys
from src.file_utils import prep_working_dir
from src.investigate_files import investigate
from src.exercise_manifest import build_manifest
from src.generate_gpx import generate_gpx_files

SUPPORTED_METHODS = ['investigate', 'manifest', 'generate']


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1].lower() == 'help':
        print(f'Use one of these methods as the first arg: {SUPPORTED_METHODS}')
        print('Followed by the path to the zip file of your samsung data')
    elif len(sys.argv) == 3:
        method = sys.argv[1].lower()
        file_path = sys.argv[2]
        if method not in SUPPORTED_METHODS:
            raise Exception(f'{method} is not a supported method ({SUPPORTED_METHODS})!')
        else:
            prep_working_dir(file_path)
        if method == 'investigate':
            investigate(file_path)
        elif method == 'manifest':
            manifest = build_manifest(file_path)
            print(f'Found these exercises to be imported: {[(key, len(value)) for key, value in manifest.items()]}')
            print('NOTE :: Not all of these will have enough GPS points to upload to Strava')
        elif method == 'generate':
            generate_gpx_files(file_path)
    else:
        raise Exception(f'Unkown args: {sys.argv[1:]}')
