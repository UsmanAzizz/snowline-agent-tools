@echo off
REM Snowline Agent Tools - CLI Wrapper
REM Auto-adds Scripts to PATH and runs CLI

REM Get Scripts path from Python
for /f "delims=" %%P in ('python -c "import sysconfig; print(sysconfig.get_path(\'scripts\'))"') do set "SNOWLINE_SCRIPTS=%%P"

REM Add to PATH for this cmd session
set "PATH=%SNOWLINE_SCRIPTS%;%PATH%"

REM Run the CLI
python -m snowline_toolkit.cli %*
