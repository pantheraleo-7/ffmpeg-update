FFmpeg-update is a package manager for the FFmpeg suite, available as both a CLI tool and a Python library. It fetches pre-built, static binaries published by [Martin Riedl](https://ffmpeg.martin-riedl.de).

> **Supported Platforms (Upstream):** Linux amd64, Linux arm64v8, macOS Intel (Deprecated), Apple Silicon

# Features

- Install [pre-built static binaries of] FFmpeg, FFprobe, and/or FFplay
- Fetch latest *release* or *snapshot* builds
- Configure custom installation location
- Update to latest version
- Check for updates
- Uninstall from system
- Smart permission handling
- Atomic file system operations
- Automatic operating system and machine architecture detection

# Installation

```bash
pip install ffmpeg-update
```

The installation provides the `ffup` executable.

# CLI Reference

## Usage

```bash
ffup <install|update [--dry-run]|check|uninstall> [OPTIONS] [ffmpeg] [ffprobe] [ffplay]
```

Alternatively, can be invoked as a module with `python -m ffmpeg_update <COMMAND>`.

> **Hint:** Multiple names can be passed, e.g. `ffup install ffmpeg ffprobe`

> **Note:** Default is `ffmpeg`, if no name is passed

## Parameters

- `--dir`: The path to the installation directory
  - Environment variable: `$FFUP_DIR`/`$XDG_BIN_HOME`
  - Default: `~/.local/bin`
  - Functions: `check`, `install`, `uninstall`, `update`

- `--build`: The build type
  - Choices: `release`, `snapshot`
  - Environment Variable: `$FFUP_BUILD`
  - Default: `snapshot`
  - Functions: `check`, `install`, `update`

- `--arch`: The machine architecture
  - Choices: `amd64`, `arm64`
  - Environment Variable: `$FFUP_ARCH`
  - Default: Auto-detect using `platform.machine()`
  - Functions: `check`, `install`, `update`

- `--os`: The operating system
  - Choices: `linux`, `macos`
  - Environment Variable: `$FFUP_OS`
  - Default: Auto-detect using `platform.system()`
  - Functions: `check`, `install`, `update`

- `--dry-run`: A flag to skip download/install, and only check for updates
  - `ffup check` is an alias for `ffup update --dry-run`
  - Default: `False`
  - Functions: `update`

# API Reference

## Functions

- `update(bins = {"ffmpeg"}, /, *, dry_run = False, dir, tempdir, progress, client) -> None`
- `install(bins = {"ffmpeg"}, /, *, dir, tempdir, progress, client) -> None`
- `uninstall(bins = {"ffmpeg"}, /, *, dir) -> None`
- `get_arch() -> Literal["amd64", "arm64"]`
- `get_os() -> Literal["linux", "macos"]`

> - `bins`: A `set` of binary names
>   - Must contain one or more of `"ffmpeg"`, `"ffprobe"`, and `"ffplay"`
>
> - `dry_run`: A `bool` indicating whether to skip download/install
>
> - `dir`: A `pathlib.Path` to the installation directory
>   - Must exist and be absolute
>
> - `tempdir`: A `tempfile.TemporaryDirectory[str]` used to store and extract the downloaded archives
>
> - `progress`: A `rich.progress.Progress` used to show progress bars in the terminal
>
> - `client`: A `niquests.Session` used to make HTTP requests
>   - Must set parameter `base_url` to `f"https://ffmpeg.martin-riedl.de/redirect/latest/{os}/{arch}/{build}/"`
>   - `build`: `"release"`, `"snapshot"`
>   - `arch`: `"amd64"`, `"arm64"`
>   - `os`: `"linux"`, `"macos"`

# Error Handling

## `FileNotFoundError`

- By design, all operations will fail if the path in question does not exist
- For new installations, ensure that the installation directory exists
- For other operations, ensure that the path points to the installed binary

## `HTTPError`

- `404 Client Error: Not Found for url: ...`
  - Caused by invalid values for one or more of `build`, `arch`, and `os` parameters

## `PermissionError`

- Triggers automatic escalation via `sudo`
- The user is prompted for a password at `stdin`
