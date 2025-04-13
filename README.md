# FFUp

A Python CLI tool to manage FFmpeg static binaries on Unix-like systems. It fetches the latest builds published by [Martin Riedl](https://ffmpeg.martin-riedl.de/).

## Features

- Install static builds of FFmpeg, FFprobe, and/or FFplay.
- Update to the latest version.
- Check for update.
- Uninstall from the system.
- Supports custom installation paths.
- Supports both **Linux** and **macOS** (Windows builds are not available upstream).

## Installation

```bash
pip install ffmpeg-update
```

## Usage

### With `ffup`:

The installation provides the `ffup` command.

- **Install**:
  ```bash
  ffup install [--dir <custom-path>]
  ```
- **Update**:
  ```bash
  ffup update [--dir <custom-path>] [--dry-run]
  ```
- **Check**:
  ```bash
  ffup check [--dir <custom-path>]
  ```
- **Uninstall**:
  ```bash
  ffup uninstall [--dir <custom-path>]
  ```

### With `python`:

Alternatively, the module can be invoked directly.

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
  - `--dry-run`: Only checks for update, skips download and install.

3. **Check**:

```bash
ffup check [--dir <custom-path>]
```

- Checks for update.
- Same as `ffup update [--dir <custom-path>] --dry-run`.
- Flags:
  - `--dir <custom-path>`: Specifies the directory where the binary is installed.
  - Defaults to the first executable found on the `$PATH`.

4. **Uninstall**:

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

- Permission error triggers automatic escalation via `sudo` [and, consequently, prompts the user for password at `stdin`].
- Path handling checks are exhaustive, with diagnostics logged to `stdout` and `stderr` as appropriate.
