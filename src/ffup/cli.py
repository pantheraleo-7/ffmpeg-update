import os as os_
import platform
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import fire
import requests
from tqdm import tqdm


class FFUp:
    def __init__(self, *, dir=None, os=None, arch=None, build=None):
        self.dir = (
            Path(
                dir
                or os_.getenv("FFUP_DIR")
                or os_.getenv("XDG_BIN_HOME")
                or "~/.local/bin"
            )
            .expanduser()
            .resolve()
        )
        self.os = (
            os
            or os_.getenv("FFUP_OS")
            or platform.system().replace("Darwin", "macOS").lower()
        )
        self.arch = (
            arch
            or os_.getenv("FFUP_ARCH")
            or ("arm64" if platform.machine() in ["arm64", "aarch64"] else "amd64")
        )
        self.build = build or os_.getenv("FFUP_BUILD") or "snapshot"
        self._TMPDIR = tempfile.TemporaryDirectory()

    def __del__(self):
        self._TMPDIR.cleanup()

    def install(self, *bins):
        for bin in self._get_bins(bins):
            url = self._get_url(bin)
            path = self.dir / bin

            print("Installing:", bin)
            file = self._download(url)
            self._install(file, path)
            print("Installed:", path)

    def uninstall(self, *bins):
        for bin in self._get_bins(bins):
            path = self.dir / bin

            print("Uninstalling:", bin)
            self._uninstall(path)
            print("Uninstalled:", path)

    def update(self, *bins, dry_run=False):
        for bin in self._get_bins(bins):
            url = self._get_url(bin)
            path = self.dir / bin

            print("Updating:" if not dry_run else "Checking:", bin)
            current_version = self._current(path)
            print("Current version:", current_version)
            latest_version = self._latest(url)
            print("Latest version:", latest_version)
            if current_version != latest_version:
                print("Update available")
                if not dry_run:
                    file = self._download(url)
                    self._install(file, path)
                    print("Updated:", path)
            else:
                print("Already up to date")

    def check(self, *bins):
        self.update(*bins, dry_run=True)

    def _get_bins(self, bins):
        return set(bins) or {os_.getenv("FFUP_BIN") or "ffmpeg"}

    def _get_url(self, bin):
        return f"https://ffmpeg.martin-riedl.de/redirect/latest/{self.os}/{self.arch}/{self.build}/{bin}.zip"

    def _current(self, path):
        output = subprocess.check_output([path, "-version"], text=True)

        match = re.search(r"version (N-\d+-\w+|\d\.\d(\.\d)?)", output)
        if match is None:
            print(
                f"Error: failed to parse current version from `{path} -version` output",
                file=sys.stderr,
            )
            sys.exit(1)

        return match.group(1)

    def _latest(self, url):
        response = requests.get(url, allow_redirects=False)

        response.raise_for_status()
        if response.status_code == 307:
            match = re.search(
                r"_(N-\d+-\w+|\d\.\d(\.\d)?)", response.headers["location"]
            )
            if match is None:
                print(
                    "Error: failed to parse latest version from HTTP response",
                    file=sys.stderr,
                )
                sys.exit(1)

            return match.group(1)
        else:
            print("Headers:", response.headers, file=sys.stderr)
            print("Error: unexpected", response, file=sys.stderr)
            sys.exit(1)

    def _download(self, url):
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            bar = tqdm(
                desc="Downloading",
                total=int(response.headers["content-length"]),
                unit="B",
                unit_scale=True,
                dynamic_ncols=True,
            )
            file = Path(self._TMPDIR.name, "ff.zip")
            with file.open("wb") as zf:
                for chunk in response.iter_content(chunk_size=4096):
                    chunk_size = zf.write(chunk)
                    bar.update(chunk_size)
        return file

    def _install(self, file, path):
        with zipfile.ZipFile(file, "r") as zf:
            bin = zf.extract(path.name, self._TMPDIR.name)
            os_.chmod(bin, 0o755)

        try:
            os_.replace(bin, path)
        except PermissionError:
            subprocess.run(["sudo", "mv", bin, path], check=True, capture_output=True)

    def _uninstall(self, path):
        try:
            os_.remove(path)
        except PermissionError:
            subprocess.run(["sudo", "rm", path], check=True, capture_output=True)


def main():
    fire.Fire(FFUp)
