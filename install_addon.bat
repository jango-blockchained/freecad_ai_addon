@echo off
REM FreeCAD AI Addon Installation Script (Windows)
REM This script creates a symlink to the addon in FreeCAD's Mod directory

setlocal enabledelayedexpansion

echo FreeCAD AI Addon Installation Script (Windows)
echo ==============================================
echo.

REM Get the current directory (should be the addon root)
set "ADDON_DIR=%~dp0"
set "ADDON_DIR=%ADDON_DIR:~0,-1%"
set "ADDON_NAME=freecad_ai_addon"

REM Default FreeCAD Mod directories
set "MOD_DIR1=%USERPROFILE%\AppData\Roaming\FreeCAD\Mod"
set "MOD_DIR2=%USERPROFILE%\.FreeCAD\Mod"
set "MOD_DIR3=C:\Program Files\FreeCAD\Mod"

REM Function to find FreeCAD Mod directory
set "FREECAD_MOD_DIR="

if exist "!MOD_DIR1!" (
    set "FREECAD_MOD_DIR=!MOD_DIR1!"
) else if exist "%USERPROFILE%\AppData\Roaming\FreeCAD" (
    mkdir "!MOD_DIR1!" 2>nul
    set "FREECAD_MOD_DIR=!MOD_DIR1!"
) else if exist "!MOD_DIR2!" (
    set "FREECAD_MOD_DIR=!MOD_DIR2!"
) else if exist "%USERPROFILE%\.FreeCAD" (
    mkdir "!MOD_DIR2!" 2>nul
    set "FREECAD_MOD_DIR=!MOD_DIR2!"
) else if exist "!MOD_DIR3!" (
    set "FREECAD_MOD_DIR=!MOD_DIR3!"
)

if "%FREECAD_MOD_DIR%"=="" (
    echo [ERROR] Could not find FreeCAD Mod directory
    echo.
    echo Please create one of these directories manually:
    echo   - %MOD_DIR1%
    echo   - %MOD_DIR2%
    echo   - %MOD_DIR3%
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo [SUCCESS] Found FreeCAD Mod directory: %FREECAD_MOD_DIR%

set "TARGET_LINK=%FREECAD_MOD_DIR%\%ADDON_NAME%"

REM Parse command line argument
set "COMMAND=%1"
if "%COMMAND%"=="" set "COMMAND=install"

if /i "%COMMAND%"=="install" goto install
if /i "%COMMAND%"=="uninstall" goto uninstall
if /i "%COMMAND%"=="check" goto check
if /i "%COMMAND%"=="help" goto help
if /i "%COMMAND%"=="-h" goto help
if /i "%COMMAND%"=="--help" goto help

echo [ERROR] Unknown command: %COMMAND%
echo.
goto help

:install
echo [INFO] Installing FreeCAD AI Addon...

REM Check if target already exists
if exist "%TARGET_LINK%" (
    REM Check if it's a directory junction/symlink
    dir "%TARGET_LINK%" | find "<JUNCTION>" >nul
    if !errorlevel! equ 0 (
        echo [WARNING] Symlink already exists: %TARGET_LINK%
        echo [INFO] Removing old symlink...
        rmdir "%TARGET_LINK%"
    ) else (
        echo [ERROR] Target exists but is not a symlink: %TARGET_LINK%
        echo [ERROR] Please remove it manually and run this script again
        pause
        exit /b 1
    )
)

REM Create the directory junction (Windows symlink equivalent)
echo [INFO] Creating symlink...
mklink /J "%TARGET_LINK%" "%ADDON_DIR%" >nul

if !errorlevel! equ 0 (
    echo [SUCCESS] Symlink created successfully!
    echo.
    echo Installation Details:
    echo   Source: %ADDON_DIR%
    echo   Target: %TARGET_LINK%
    echo.
    echo The addon should now appear in FreeCAD's Addon Manager or Workbench list.
) else (
    echo [ERROR] Failed to create symlink
    echo [ERROR] Make sure you're running as Administrator
    pause
    exit /b 1
)
goto end

:uninstall
echo [INFO] Uninstalling FreeCAD AI Addon...

if exist "%TARGET_LINK%" (
    dir "%TARGET_LINK%" | find "<JUNCTION>" >nul
    if !errorlevel! equ 0 (
        echo [INFO] Removing symlink: %TARGET_LINK%
        rmdir "%TARGET_LINK%"
        echo [SUCCESS] Symlink removed
    ) else (
        echo [WARNING] Found non-symlink at: %TARGET_LINK%
        echo [WARNING] Please remove it manually
    )
) else (
    echo [WARNING] No symlink found to remove
)
goto end

:check
echo [INFO] Checking installation status...

if exist "%TARGET_LINK%" (
    dir "%TARGET_LINK%" | find "<JUNCTION>" >nul
    if !errorlevel! equ 0 (
        echo [SUCCESS] Found symlink: %TARGET_LINK%
        dir "%TARGET_LINK%" | find "%ADDON_DIR%" >nul
        if !errorlevel! equ 0 (
            echo [SUCCESS] Symlink points to current directory
        ) else (
            echo [WARNING] Symlink points to different directory
        )
    ) else (
        echo [WARNING] Found non-symlink at: %TARGET_LINK%
    )
) else (
    echo [INFO] No installation found
)
goto end

:help
echo Usage: %0 [install^|uninstall^|check^|help]
echo.
echo Commands:
echo   install    - Install the addon by creating a symlink (default)
echo   uninstall  - Remove the addon symlink
echo   check      - Check current installation status
echo   help       - Show this help message
echo.
echo The addon will be installed to:
echo   %FREECAD_MOD_DIR%\%ADDON_NAME%
echo.
goto end

:end
echo.
echo [INFO] Done!
pause
