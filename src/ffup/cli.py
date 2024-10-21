import os
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import fire
import requests
from tqdm import tqdm

_TEMPFILE = Path('_ff.zip')


class FFUp:

    def __init__(self, sys=None, arch=None, repo=None, bin=None):
        self.sys = sys or os.getenv('SYS') \
            or platform.system().replace('Darwin', 'macOS').lower()

        self.arch = arch or os.getenv('ARCH') \
            or ('arm64' if  platform.machine() in ['arm64', 'aarch64'] else 'amd64')

        self.repo = repo or os.getenv('REPO') or 'snapshot'
        self.bin = bin or os.getenv('BIN') or 'ffmpeg'

        self.URL = f'https://ffmpeg.martin-riedl.de/redirect/latest/{self.sys}/{self.arch}/{self.repo}/{self.bin}.zip'

    def update(self, path=None, dry_run=False):
        if path is None:
            bin = shutil.which(self.bin)
            if bin is None:
                print('Error: failed to locate the installation.')
                sys.exit(1)
            else:
                path = Path(bin).parent
        else:
            path = Path(path).expanduser()

        self._current(path/self.bin)
        self._latest()
        if self.current_version!=self.latest_version:
            if not dry_run:
                self._download()
                self._install(path)
        else:
            print('Already up to date.')

    def install(self, path='~/.local/bin'):
        path = Path(path).expanduser()

        if shutil.which(self.bin) is not None:
            print('Warning: found an existing installation on the `PATH`.')

        if (path/self.bin).exists():
            print('Error: found an existing installation at the given path.')
            sys.exit(1)

        self._latest()
        self._download()
        self._install(path)

    def _current(self, bin):
        if not bin.exists():
            print('Error: no installation found.')
            sys.exit(1)

        result = subprocess.check_output([bin, '-version'], text=True)
        match = re.search(r'version (N-\d+-\w+|\d\.\d)', result)
        if match is None:
            print(f'Error: failed to parse current version from `{bin} -version` output.')
            sys.exit(1)

        self.current_version = match.group(1)
        print('Current version:', self.current_version)

    def _latest(self):
        response = requests.get(self.URL, allow_redirects=False)
        response.raise_for_status()

        if response.status_code==307:
            redirect_url = response.headers['location']
            match = re.search(r'_(N-\d+-\w+|\d\.\d)', redirect_url)
            if match is None:
                print('Error: failed to parse latest version from redirected url.')
                sys.exit(1)

            self.latest_version = match.group(1)
            print('Latest version:', self.latest_version)
        else:
            print('Error: unexpected', response)
            print('Headers:', response.headers)
            sys.exit(1)

    def _download(self):
        with requests.get(self.URL, stream=True) as response:
            response.raise_for_status()
            bar = tqdm(
                total=int(response.headers['content-length']),
                unit='B', unit_scale=True,
                desc='Downloading', dynamic_ncols=True
            )
            with open(_TEMPFILE, 'wb') as zf:
                for chunk in response.iter_content(chunk_size=4096):
                    chunk_size = zf.write(chunk)
                    bar.update(chunk_size)

    def _install(self, path):
        with zipfile.ZipFile(_TEMPFILE, 'r') as zf:
            bin = zf.extract(self.bin)
            os.chmod(bin, 0o755)
            try:
                shutil.move(bin, path)
            except PermissionError:
                subprocess.run(['sudo', 'mv', bin, path])

        print('Successfully installed to:', path)


def main():
    try:
        fire.Fire(FFUp)
    finally:
        _TEMPFILE.unlink(missing_ok=True)
