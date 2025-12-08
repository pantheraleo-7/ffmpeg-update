import io
import os
import platform
import re
import subprocess
import zipfile
from tempfile import TemporaryDirectory
from typing import Annotated, Literal

from cyclopts import App, Parameter
from cyclopts.types import ResolvedExistingDirectory
from niquests import Session
from rich import print
from rich.progress import Progress

__all__ = ["get_arch", "get_os", "install", "uninstall", "update"]

DIR_DEFAULT = ResolvedExistingDirectory(os.path.expanduser("~/.local/bin"))

BinType = Literal["ffmpeg", "ffprobe", "ffplay"]
BuildType = Literal["release", "snapshot"]
ArchType = Literal["amd64", "arm64"]
OSType = Literal["linux", "macos"]

app = App()
app.register_install_completion_command(add_to_startup=False)


@app.meta.default
def ffup(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    dir: Annotated[
        ResolvedExistingDirectory, Parameter(env_var=("FFUP_DIR", "XDG_BIN_HOME"))
    ] = DIR_DEFAULT,
    build: Annotated[BuildType, Parameter(env_var="FFUP_BUILD")] = "snapshot",
    arch: Annotated[ArchType, Parameter(env_var="FFUP_ARCH")] | None = None,
    os: Annotated[OSType, Parameter(env_var="FFUP_OS")] | None = None,
):
    command, bound, ignored = app.parse_args(tokens)
    additional_kwargs = {}

    if "dir" in ignored:
        additional_kwargs["dir"] = dir

    if "tempdir" in ignored:
        additional_kwargs["tempdir"] = TemporaryDirectory()

    if "progress" in ignored:
        additional_kwargs["progress"] = Progress(transient=True)

    if "client" in ignored:
        arch = get_arch() if arch is None else arch
        os = get_os() if os is None else os

        additional_kwargs["client"] = Session(
            base_url=f"https://ffmpeg.martin-riedl.de/redirect/latest/{os}/{arch}/{build}/"
        )

    return command(*bound.args, **bound.kwargs, **additional_kwargs)


@app.command
def update(
    bins: set[BinType] = {"ffmpeg"},
    /,
    *,
    dry_run: Annotated[bool, Parameter(show_default=False, negative="")] = False,
    dir: Annotated[ResolvedExistingDirectory, Parameter(parse=False)],
    tempdir: Annotated[TemporaryDirectory[str], Parameter(parse=False)],
    progress: Annotated[Progress, Parameter(parse=False)],
    client: Annotated[Session, Parameter(parse=False)],
) -> None:
    with progress:
        for bin in bins:
            path = dir / bin
            current = _current(path)
            latest = _latest(bin, client)
            print(f"FF{bin[2:]}:\n\tCurrent: {current}\n\tLatest: {latest}")
            if current != latest:
                print(f"FF{bin[2:]}: update available")
                if not dry_run:
                    file = _download(bin, tempdir, progress, client)
                    _install(file, path)
                    print("Updated:", path)
            else:
                print(f"FF{bin[2:]}: up to date")


@app.command
def check(
    bins: set[BinType] = {"ffmpeg"},
    /,
    *,
    dir: Annotated[ResolvedExistingDirectory, Parameter(parse=False)],
    tempdir: Annotated[TemporaryDirectory[str], Parameter(parse=False)],
    progress: Annotated[Progress, Parameter(parse=False)],
    client: Annotated[Session, Parameter(parse=False)],
):
    update(
        bins, dry_run=True, dir=dir, tempdir=tempdir, progress=progress, client=client
    )


@app.command
def install(
    bins: set[BinType] = {"ffmpeg"},
    /,
    *,
    dir: Annotated[ResolvedExistingDirectory, Parameter(parse=False)],
    tempdir: Annotated[TemporaryDirectory[str], Parameter(parse=False)],
    progress: Annotated[Progress, Parameter(parse=False)],
    client: Annotated[Session, Parameter(parse=False)],
) -> None:
    with progress:
        for bin in bins:
            path = dir / bin
            file = _download(bin, tempdir, progress, client)
            _install(file, path)
            print("Installed:", path)


@app.meta.command
def uninstall(
    bins: set[BinType] = {"ffmpeg"},
    /,
    *,
    dir: Annotated[
        ResolvedExistingDirectory, Parameter(env_var=("FFUP_DIR", "XDG_BIN_HOME"))
    ] = DIR_DEFAULT,
) -> None:
    for bin in bins:
        path = dir / bin
        _uninstall(path)
        print("Uninstalled:", path)


def get_arch() -> ArchType:
    arch = platform.machine()
    if arch in ("x86_64", "amd64"):
        return "amd64"
    elif arch in ("aarch64", "arm64"):
        return "arm64"
    else:
        raise RuntimeError(f"unsupported architecture '{arch}'")


def get_os() -> OSType:
    os = platform.system()
    if os == "Linux":
        return "linux"
    elif os == "Darwin":
        return "macos"
    else:
        raise RuntimeError(f"unsupported operating system '{os}'")


def _current(path):
    output = subprocess.check_output([path, "-version"], text=True)
    match = re.search(r"version (N-\d+-\w+|\d\.\d(\.\d)?)", output)
    if match is None:
        raise ValueError(f"failed to parse version from `{path} -version` output")
    return match.group(1)


def _latest(bin, client):
    response = client.get(f"{bin}.zip", allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 307:
        match = re.search(r"_(N-\d+-\w+|\d\.\d(\.\d)?)", response.headers["location"])
        if match is None:
            raise ValueError("failed to parse version from HTTP response")
        return match.group(1)
    else:
        raise ValueError(f"unexpected {response}")


def _download(bin, tempdir, progress, client):
    response = client.get(f"{bin}.zip", stream=True)
    response.raise_for_status()
    id = progress.add_task(
        f"FF{bin[2:]}:", total=int(response.headers["content-length"])
    )
    with io.BytesIO() as buf:
        for chunk in response.iter_content():
            chunk_size = buf.write(chunk)
            progress.update(id, advance=chunk_size)
        progress.update(id, visible=False)
        with zipfile.ZipFile(buf) as zf:
            return zf.extract(bin, tempdir.name)


def _install(file, path):
    os.chmod(file, 0o755)
    try:
        os.replace(file, path)
    except PermissionError:
        subprocess.run(["sudo", "mv", file, path], check=True, capture_output=True)


def _uninstall(path):
    try:
        os.remove(path)
    except PermissionError:
        subprocess.run(["sudo", "rm", path], check=True, capture_output=True)


def main():
    app.meta()
