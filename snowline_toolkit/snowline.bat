@echo off
REM Snowline Agent Tools
REM Direct wrapper that finds Python and runs the CLI module

for %%P in (python python3) do (
    %%P -m snowline_toolkit.cli %*
    if not errorlevel 1 goto :eof
)
echo [ERROR] Python not found. Please install Python 3.7+
exit /b 1
