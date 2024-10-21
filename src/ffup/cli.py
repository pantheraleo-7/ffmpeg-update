import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dry-run', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-f', '--force', '-i', '--install', action='store_true')
parser.add_argument('-p', '--path', type=lambda path: Path(path).expanduser())
parser.add_argument('-o', '--os', default='macos', choices=['macos', 'linux'])
parser.add_argument('-a', '--arch', default='arm64', choices=['arm64', 'amd64'])
parser.add_argument('-r', '--repo', default='snapshot', choices=['snapshot', 'release'])
parser.add_argument('-b', '--bin', default='ffmpeg', choices=['ffmpeg', 'ffprobe', 'ffplay'])
parser.add_argument('--RE-RUN', action='store_true', help=argparse.SUPPRESS)
args = parser.parse_args()

if args.path is None:
    args.path = Path(shutil.which(args.bin)).parent

# Configurations
URL = f'https://ffmpeg.martin-riedl.de/redirect/latest/{args.os}/{args.arch}/{args.repo}/{args.bin}.zip'
TEMP_FILE = Path('__ff.zip')


def get_current_version():
    result = subprocess.check_output([args.path/args.bin, '-version'], text=True)
    match = re.search(r'version (N-\d+-\w+|\d\.\d)', result)
    if match is None:
        print(f'Failed to parse current version from `{args.path/args.bin} -version` output.')
        sys.exit(1)

    version = match.group(1)
    print('Current version:', version)
    return version


def get_latest_version():
    response = requests.get(URL, allow_redirects=False)
    response.raise_for_status()

    if response.status_code==307:
        redirect_url = response.headers['location']
        match = re.search(r'_(N-\d+-\w+|\d\.\d)', redirect_url)
        if match is None:
            print('Failed to parse latest version from redirected url.')
            sys.exit(1)

        version = match.group(1)
        print('Latest version:', version)
        return version
    else:
        print('Unexpected:', response)
        print('Headers:', response.headers)
        sys.exit(1)


def download():
    with requests.get(URL, stream=True) as response:
        response.raise_for_status()
        bar = tqdm(
            desc='Downloading',
            total=int(response.headers['content-length']),
            unit='B',
            unit_scale=True,
            dynamic_ncols=True
        )
        with open(TEMP_FILE, 'wb') as zf:
            for chunk in response.iter_content(chunk_size=4096):
                chunk_size = zf.write(chunk)
                bar.update(chunk_size)


def install():
    with zipfile.ZipFile(TEMP_FILE, 'r') as zf:
        zf.extract(args.bin, args.path)
        if args.verbose or len(zf.namelist())>1:
            zf.printdir()

    os.chmod(args.path/args.bin, 0o755)  # Make executable
    print('Successfully installed to:', args.path)


def download_n_install_w_options():
    if not args.RE_RUN:
        if not args.force and get_current_version()==get_latest_version():
            print('Already up to date.')
            return
        if args.dry_run:
            return

        download()

    try:
        install()
    except PermissionError:
        if args.RE_RUN:
            raise
        print('Installing with sudo...')
        subprocess.run(['sudo', sys.executable, *sys.argv, '--RE-RUN'])


def main():
    try:
       download_n_install_w_options()
    finally:
       TEMP_FILE.unlink(missing_ok=True)
