@echo off
setlocal EnableExtensions EnableDelayedExpansion

@REM Locate repo root
set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%\..

@REM Normalize path
pushd "%REPO_ROOT%"

@REM Ensure pkg is visible as a module root, and DO NOT inherit PYTHONPATH
set PYTHONPATH=%REPO_ROOT%\pkg

@REM Debug log (optional)
@REM echo [pkms] REPO_ROOT=%REPO_ROOT% >> "%TEMP%\pkms-dispatch.log"
@REM echo [pkms] ARGS=%* >> "%TEMP%\pkms-dispatch.log"

@REM Launch via module
uv run python -m pkms %*
set EXITCODE=%ERRORLEVEL%

popd
exit /b %EXITCODE%