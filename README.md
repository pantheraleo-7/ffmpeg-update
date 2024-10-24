# FFUp: **FF**mpeg **Up**date

**ffmpeg-update** is a Python package designed to manage FFmpeg static binaries on **macOS** and **Linux**. It fetches the latest builds published by [Martin Riedl](https://ffmpeg.martin-riedl.de/).

## Features

- Install static builds of FFmpeg, FFprobe, and/or FFplay.
- Update to the latest version.
- Uninstall from the system.
- Supports custom installation paths.
- Supports both **Linux** and **macOS** (Windows builds are not available upstream).

## Installation

### Using `uv`:
```bash
uv tool install git+https://github.com/pantheraleo-7/ffmpeg-update
```

### Using `pip`:
```bash
pip install git+https://github.com/pantheraleo-7/ffmpeg-update
```

## Usage

### With `ffup`:
After installation, the `ffup` command becomes available in the terminal.
- **Install**:
  ```bash
  ffup install [--dir <custom-path>]
  ```
- **Update**:
  ```bash
  ffup update [--dir <custom-path>] [--dry-run]
  ```
- **Uninstall**:
  ```bash
  ffup uninstall [--dir <custom-path>]
  ```

### With `python`:
Alternatively, the package can be run as a CLI module:
```bash
python -m ffup <command>
```

## Documentation

### CLI Commands, Their Flags and Environment Variables

1. **Install**:
   ```bash
   ffup install [--dir <custom-path>]
   ```
   - Downloads and installs the binary.
   - Flags and Environment variables:
     - `--dir <custom-path>`: Specifies the installation directory.
     - `$XDG_BIN_HOME`: Used as the installation directory if `--dir` is not specified.
     - Defaults to `~/.local/bin` if none of the above is defined.

2. **Update**:
   ```bash
   ffup update [--dir <custom-path>] [--dry-run]
   ```
   - Updates the binary to the latest version.
   - Flags:
     - `--dir <custom-path>`: Specifies the directory where the binary is installed.
     - Defaults to the first executable found on the `$PATH`.
     - `--dry-run`: Only checks for updates, skips download and install.

3. **Uninstall**:
   ```bash
   ffup uninstall [--dir <custom-path>]
   ```
   - Removes the installed binary.
   - Flags:
     - `--dir <custom-path>`: Specifies the directory where the binary is installed.
     - Defaults to the first executable found on the `$PATH`.

### Global Flags and Their Environment Variables

- `--sys` or `$FF_SYS`: Specifies the platform name (`macos`, `linux`). Default is to detect using `platform` stdlib.
- `--arch` or `$FF_ARCH`: Specifies the platform architecture (`arm64`, `amd64`). Default is to detect using `platform` stdlib.
- `--repo` or `$FF_REPO`: Specifies the static build type (`snapshot`, `release`). Defaults to `snapshot`.
- `--bin` or `$FF_BIN`: Specifies the binary name (`ffmpeg`, `ffprobe`, `ffplay`). Defaults to `ffmpeg`.

> **Note:** Flags have precedence over their respective environment variables.

> **Note:** Command arguments may be given positionally. Global arguments are always specified with their respective keywords (flags).

### Error Handling

- Permission issues are resolved automatically with `sudo` when necessary (and, consequently, user is prompted for password at `stdin`).
- Checks for path handling are exhaustive, with appropriate messages written to `stdout`.
