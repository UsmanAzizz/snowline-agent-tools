@echo off
REM Snowline Agent Tools - Simple Launcher
REM Just finds python and runs the module

REM Get Python path
where python >nul 2>&1
if %ERRORLEVEL%==0 (
    python -m snowline_toolkit.cli %*
) else (
    REM Try py launcher
    py -m snowline_toolkit.cli %*
)
