import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import fire
import requests
from tqdm import tqdm


class FFUp:
    def __init__(self, sys=None, arch=None, repo=None, bin=None):
        self.sys = sys or os.getenv('FF_SYS') \
            or platform.system().replace('Darwin', 'macOS').lower()

        self.arch = arch or os.getenv('FF_ARCH') \
            or ('arm64' if  platform.machine() in ['arm64', 'aarch64'] else 'amd64')

        self.repo = repo or os.getenv('FF_REPO') or 'snapshot'
        self.bin = bin or os.getenv('FF_BIN') or 'ffmpeg'

        self.URL = f'https://ffmpeg.martin-riedl.de/redirect/latest/{self.sys}/{self.arch}/{self.repo}/{self.bin}.zip'
        self._TMPDIR = tempfile.TemporaryDirectory()

    def __del__(self):
        self._TMPDIR.cleanup()

    def check(self, dir=None):
        self.update(dir=dir, dry_run=True)

    def install(self, dir=None):
        path = Path(dir or os.getenv('XDG_BIN_HOME') or os.path.expanduser('~/.local/bin'), self.bin)

        if shutil.which(self.bin) is not None:
            print('Warning: found an existing installation on the `PATH`.')

        if path.exists():
            print('Error: found an existing installation at the given path.', file=sys.stderr)
            sys.exit(1)

        self._latest()
        file = self._download()
        self._install(file, path)

    def update(self, dir=None, dry_run=False):
        path = self._getpath(dir)
        self._current(path)
        self._latest()
        if self.current_version!=self.latest_version:
            print('Update available.')
            if not dry_run:
                file = self._download()
                self._install(file, path)
        else:
            print('Already up to date.')

    def uninstall(self, dir=None):
        path = self._getpath(dir)
        self._uninstall(path)

    def _getpath(self, dir):
        if dir is None:
            path = shutil.which(self.bin)
            if path is None:
                print('Error: no installation found on the `PATH`.', file=sys.stderr)
                sys.exit(1)
        else:
            path = Path(dir, self.bin)
            if not path.exists():
                print('Error: no installation found at the given path.', file=sys.stderr)
                sys.exit(1)

        return Path(path)

    def _current(self, path):
        output = subprocess.check_output([path, '-version'], text=True)

        match = re.search(r'version (N-\d+-\w+|\d\.\d)', output)
        if match is None:
            print(f'Error: failed to parse current version from `{path} -version` output.', file=sys.stderr)
            sys.exit(1)

        self.current_version = match.group(1)
        print('Current version:', self.current_version)

    def _latest(self):
        response = requests.get(self.URL, allow_redirects=False)
        response.raise_for_status()

        if response.status_code==307:
            match = re.search(r'_(N-\d+-\w+|\d\.\d)', response.headers['location'])
            if match is None:
                print('Error: failed to parse latest version from redirected url.', file=sys.stderr)
                sys.exit(1)

            self.latest_version = match.group(1)
            print('Latest version:', self.latest_version)

        else:
            print('Error: unexpected', response, file=sys.stderr)
            print('Headers:', response.headers, file=sys.stderr)
            sys.exit(1)

    def _download(self):
        with requests.get(self.URL, stream=True) as response:
            response.raise_for_status()
            bar = tqdm(
                total=int(response.headers['content-length']),
                unit='B', unit_scale=True,
                desc='Downloading', dynamic_ncols=True
            )
            file = Path(self._TMPDIR.name, 'ff.zip')
            with file.open('wb') as zf:
                for chunk in response.iter_content(chunk_size=4096):
                    chunk_size = zf.write(chunk)
                    bar.update(chunk_size)
        return file

    def _install(self, file, path):
        with zipfile.ZipFile(file, 'r') as zf:
            bin = zf.extract(self.bin, self._TMPDIR.name)
            os.chmod(bin, 0o755)

        try:
            os.replace(bin, path)
        except PermissionError:
            subprocess.run(['sudo', 'mv', bin, path], check=True, capture_output=True)

        print('Successfully installed:', path)

    def _uninstall(self, path):
        try:
            os.remove(path)
        except PermissionError:
            subprocess.run(['sudo', 'rm', path], check=True, capture_output=True)

        print('Successfully uninstalled:', path)


def main():
    fire.Fire(FFUp)
