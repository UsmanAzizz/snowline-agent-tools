@echo off
REM Snowline Agent Tools - CLI Wrapper
REM Runs the snowline CLI without needing PATH setup

REM Use py launcher if available (handles multiple Python versions)
where py >nul 2>&1
if %errorlevel%==0 (
    py -m snowline_toolkit.cli %*
) else (
    python -m snowline_toolkit.cli %*
)
