import re
import os
import argparse
import requests
from tqdm import tqdm
from config import variables, rasters, presence_only, presence_absence, metadata, url_struct


def find_url(file):
    """Given the folder and the file, return the url to download the file

    Args:
        category (str): folder containing the file
        file (str): file to download

    Raises:
        requests.exceptions.HTTPError: exception raised when the url is not found

    Returns:
        str: the url to direct download the file
    """
    response = requests.get(url_struct.format(file), timeout=60)
    url_key = "rawPath"
    pattern = f"{url_key}: '([^']+)'"
    match = re.search(pattern, response.text)

    if match:
        return match.group(1).replace('\\u002D', '-') + '?raw=1'

    raise requests.exceptions.HTTPError(f'Failed to find url for {file}')


def check_if_file_complete(path, response):
    """Given a path and a response from a request returns True or False
    if the file needs to be re-downloaded...

    Args:
        path (str): the location of the file on disk
        response (requests.models.Response): the response to the file request

    Returns:
        bool: True if the file needs to be downloaded, False otherwise.
    """
    if os.path.exists(path):
        file_size_server = int(response.headers.get('Content-Length', 0))
        file_size_downloaded = os.path.getsize(path)
        if file_size_server != file_size_downloaded:
            return True
        else:
            print(f'{path} already downloaded and complete.')
            return False
    else:
        return True


def download_file(url, filename):
    """Download a file given an url.

    Args:
        url (str): the url of the file to download
        filename (str): the location where to write the file
    """
    response = requests.get(url, timeout=60, stream=True)
    assert response.status_code == 200, 'Failed to download file'

    if check_if_file_complete(filename, response):
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        with open(filename, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()

        if total_size_in_bytes not in (0, progress_bar.n):
            raise requests.exceptions.RequestException('Error.. size do not match...')


def process_download(file, data):
    """Download the file in category cat into the folder data. The function
    handles the exception that can rise from the sub-methods.

    Args:
        cat (str): the folder containing the file
        file (str): the file itself
        data (str): the folder to save the data in
    """
    try:
        u = find_url(file)
        print(f'Downloading {u} ({file})')
        download_file(u, os.path.join(data, file))
    except requests.exceptions.HTTPError:
        print(f'Failed to find url for {file}')
    except (AssertionError, requests.exceptions.RequestException):
        print(f'Failed to download file {file}\n\t{u}')


def process_option(struct, cubes, variable, output):
    """Process download options for a given structure and variable.

    Args:
        struct (dict): Data structure specifying file paths
        cubes (bool): Whether to download cubes if available
        variable (str): The variable to process
        output (str): Output directory for the files
    """
    if variable in struct:
        files = struct[variable].get('cubes' if cubes else 'not_cubes', [])
        for f in files:
            process_download(f, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            'GeoPlant Dataset Downloader.\n'
            'This script allows you to download individual files or entire datasets. '
            'You can choose between full raster data, presence-only or presence-absence metadata, '
            'and pre-extracted data, with an option to select variables of interest.'
        )
    )
    parser.add_argument('--data', default='data',
                        help='Destination directory for all downloaded files (default: "data").')

    group = parser.add_argument_group('Data type')
    group.add_argument(
        '--metadata', action='store_true',
        help='Download metadata for both presence-only (PO) and presence-absence (PA) data.'
    )
    group.add_argument(
        '--rasters', action='store_true',
        help='Download complete raster datasets for the selected variables.'
    )
    group.add_argument(
        '--presence-only', action='store_true',
        help='Download pre-extracted data for presence-only occurrences.'
    )
    group.add_argument(
        '--presence-absence', action='store_true',
        help='Download pre-extracted data for presence-absence surveys.'
    )
    group.add_argument(
        '--pre-extracted', action='store_true',
        help=(
            'Download pre-extracted data for the selected variables. '
            'Works in conjunction with "--presence-only" and/or "--presence-absence" options.'
        )
    )
    group.add_argument(
        '--cube', action='store_true',
        help='Download cube files (compressed formats) instead of CSV files when available.'
    )

    group = parser.add_argument_group('Variables')
    for v in variables:
        group.add_argument(
            f'--{v}', action='store_true',
            help=f'Download data specifically related to the "{v}" variable.'
        )
    group.add_argument(
        '--all-variables', action='store_true',
        help='Select all variables for download, overriding individual variable selections.'
    )

    args = parser.parse_args()

    os.makedirs(args.data, exist_ok=True)

    # Download metadata
    if args.metadata:
        if args.presence_only or not (args.presence_only or args.presence_absence):
            for f in metadata['po']:
                print("Downloading presence-only metadata...")
                process_download(f, args.data)

        if args.presence_absence or not (args.presence_only or args.presence_absence):
            for f in metadata['pa']:
                print("Downloading presence-absence metadata...")
                process_download(f, args.data)

    # Download rasters
    if args.rasters:
        for v in variables:
            if args.all_variables or getattr(args, v):
                if v in rasters:
                    print(f"Downloading raster data for variable '{v}'...")
                    process_download(rasters[v], args.data)

    # Download pre-extracted data
    if args.pre_extracted:
        for v in variables:
            if args.all_variables or getattr(args, v):
                if args.presence_only:
                    print(f"Downloading pre-extracted presence-only data for variable '{v}'...")
                    process_option(presence_only, args.cube, v, args.data)
                if args.presence_absence:
                    print(f"Downloading pre-extracted presence-absence data for variable '{v}'...")
                    process_option(presence_absence, args.cube, v, args.data)
