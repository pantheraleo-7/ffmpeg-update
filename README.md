# FFUp

A CLI package manager for the FFmpeg suite. It supports installation, updating, and management of pre-built static binaries published by [Martin Riedl](https://ffmpeg.martin-riedl.de/).

## Features

- Install [pre-built static binaries of] FFmpeg, FFprobe, and/or FFplay
- Fetch latest `release` or `snapshot` builds
- Configure custom installation location
- Update to latest version
- Check for updates
- Uninstall from system
- Smart permission handling
- Atomic file system operations
- Progress bar with ETA and download speed
- Automatic operating system and machine architecture detection

> **Supported Platforms (Upstream):** Linux amd64, Linux arm64v8, macOS Intel (Deprecated), Apple Silicon

## Installation

FFUp is available in and as `ffmpeg-update` python package on PyPI.

```bash
pip install ffmpeg-update
```

> **Note:** you may have to activate the virtual environment or put the `bin` directory in `$PATH`

## CLI Reference

### Usage

The installation provides the `ffup` executable.

```bash
ffup [OPTIONS] <install|update|check|uninstall> [ffpmeg] [ffprobe] [ffplay]
```

> **Hint:** you can pass multiple names to the commands, e.g. `ffup install ffmpeg ffprobe`

Alternatively, it can also be invoked using `python -m`.

```bash
python -m ffup [OPTIONS] <install|update|check|uninstall>
```

### Commands

- **Install**:
  ```bash
  ffup install [ffpmeg] [ffprobe] [ffplay]
  ```
- **Update**:
  ```bash
  ffup update [--dry-run] [ffpmeg] [ffprobe] [ffplay]
  ```
- **Check**:
  ```bash
  ffup check [ffpmeg] [ffprobe] [ffplay]
  ```
- **Uninstall**:
  ```bash
  ffup uninstall [ffpmeg] [ffprobe] [ffplay]
  ```

> **Note:** if you do not pass any name, e.g. `ffup install`, all commands will default to `ffmpeg`

## Documentation

### Syntax

```bash
ffup [--dir <PATH>] [--os <linux|macos>] [--arch <arm64|amd64>] [--build <snapshot|release>] <install|update [--dry-run]|check|uninstall> [ffpmeg] [ffprobe] [ffplay]
```

### Global Options and Environment Variables

> **Note:** the environment variables and defaults are listed in order of precedence

```bash
ffup [--dir <PATH>]
```

- Specifies the installation directory
  - `$FFUP_DIR`
  - `$XDG_BIN_HOME`
  - Defaults to `~/.local/bin`

```bash
ffup [--build <snapshot|release>]
```

- Specifies the build type
  - `$FFUP_BUILD`
  - Defaults to `snapshot`.

```bash
ffup [--os <linux|macos>]
```

- Specifies the operating system
  - `$FFUP_OS`
  - Defaults to auto-detection using `platform` stdlib

```bash
ffup [--arch <arm64|amd64>]
```

- Specifies the machine architecture
  - `$FFUP_ARCH`
  - Defaults to auto-detection using `platform` stdlib

### Command Flags

```bash
ffup update [--dry-run]
```

- Checks for updates but stops before downloading and installing
- `ffup check` is an alias for `ffup update --dry-run`

### Error Handling

- `PermissionError`
  - Triggers automatic escalation via `sudo`
  - The user is prompted for a password at `stdin`
- `FileNotFoundError`
  - By design, all commands will fail if the path in question does not exist
  - If the error occurs in the `ffup install` command, use `mkdir -p <PATH>` to create the installation directory
  - If the error occurs in any other command, ensure the path points to the installed binary
- `requests.exceptions.HTTPError`
  - `404 Client Error: Not Found for url: ...`
    - Caused by invalid input value for an option or argument
    - Ensure the values are correct
