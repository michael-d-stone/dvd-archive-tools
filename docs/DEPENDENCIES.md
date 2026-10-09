# Dependencies

This document records the external software used to build, run, and test
disc-archive-tools.

The versions listed below are the versions used during development and
regression testing on Debian 12. They are not necessarily minimum supported
versions.

## DVD-specific dependencies

### libdvdread

- Tested version: 6.1.3
- Debian packages: libdvdread8, libdvdread-dev
- License: GPL-2.0-or-later, with separately licensed files in the upstream
  source distribution
- Use: linked directly into `dvd-ifo-dump`
- Source use:
  - `<dvdread/dvd_reader.h>`
  - `<dvdread/ifo_read.h>`
- Build linkage: `-ldvdread`

`src/ifo_dump.c` uses the public libdvdread API to inspect DVD IFO structures
and enumerate playable menu PGC candidates.

### libdvdnav

- Tested version: 6.1.1
- Debian packages: libdvdnav4, libdvdnav-dev
- License: GPL-2.0-or-later, with separately licensed files in the upstream
  source distribution
- Use: dependency of the project's DVD-enabled FFmpeg build
- Not linked directly into disc-archive-tools code

### FFmpeg

- Tested version: 9.0.1
- License of tested build: GPL-2.0-or-later
- Use: external `ffmpeg` and `ffprobe` executables
- Not linked directly into disc-archive-tools code

The tested FFmpeg build was configured as:

    --prefix=/opt/ffmpeg-dvd
    --enable-gpl
    --enable-libdvdread
    --enable-libdvdnav

The project requires FFmpeg with the `dvdvideo` demuxer and the DVD support
needed by the extraction scripts.

FFmpeg performs lossless stream-copy extraction of DVD titles and menu
content. ffprobe is used to inspect and verify extracted Matroska files.

### lsdvd

- Tested version: 0.17
- Debian package: lsdvd
- License: GNU GPL version 2
- Use: external executable
- Not linked into disc-archive-tools code

`dvd-title-extract` uses lsdvd to enumerate DVD titles before extraction.

## Runtime dependencies

### Bash

- Tested version: 5.2.15
- Use: interpreter for the shell scripts

### Python 3

- Tested version: 3.11.2
- Use: interpreter for `dvd-verify` and the regression test harness
- Third-party Python packages: none

The Python programs currently use only the standard library.

### awk

- Tested implementation: GNU awk 5.2.1
- Use: parses lsdvd output when determining the DVD title count

### Standard Unix utilities

The shell scripts and Makefile use ordinary system utilities including:

- mkdir
- rm
- install
- dirname

On the Debian 12 development system these are provided by GNU coreutils where
applicable.

## Build and test dependencies

### GNU Make

- Tested version: 4.3
- Use: build, installation, cleanup, and regression-test orchestration

### C compiler

- Tested compiler: GCC 12.2.0
- Use: builds `src/ifo_dump.c`

### C library

- Tested environment: Debian glibc 2.36
- Use: normal C runtime and standard library

## Dependency relationship

disc-archive-tools currently contains no vendored copies of FFmpeg,
libdvdread, libdvdnav, lsdvd, Bash, Python, GNU awk, GNU Make, GCC, or
GNU coreutils.

The important dependency relationships are:

- `dvd-ifo-dump` is compiled and linked against libdvdread.
- FFmpeg and ffprobe are invoked as separate executables.
- lsdvd is invoked as a separate executable.
- Bash and Python are script interpreters.
- awk and standard Unix utilities are invoked as separate commands.
- libdvdnav is used by the required DVD-enabled FFmpeg build rather than
  directly by disc-archive-tools.

## Provenance and licensing

This dependency inventory is part of the project's release audit.

Before the first release, the project license, required notices, upstream
attribution, redistribution requirements, and any source-derived material
must be reviewed against the licenses of the dependencies above.

The existence of a dependency in this document does not by itself imply that
its license applies to every file in disc-archive-tools.
