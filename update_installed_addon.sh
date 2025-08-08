#!/bin/bash

# This script updates the installed version of the addon with the latest changes
# from the Git repository

# Path to the Git repository
REPO_DIR="$(pwd)"

# Path to the installed addon directory
INSTALLED_DIR="/home/jango/.local/share/FreeCAD/Mod/freecad_ai_addon"

# Make sure we're in the right directory
if [ ! -f "${REPO_DIR}/InitGui.py" ]; then
  echo "Error: InitGui.py not found in current directory"
  echo "Please run this script from the root of the freecad_ai_addon repository"
  exit 1
fi

# Check if the installed directory exists
if [ ! -d "${INSTALLED_DIR}" ]; then
  echo "Error: Installed addon directory not found at ${INSTALLED_DIR}"
  exit 1
fi

echo "Updating installed addon with latest changes from Git repository..."
echo "Source: ${REPO_DIR}"
echo "Target: ${INSTALLED_DIR}"

# Copy the critical files
cp -v "${REPO_DIR}/InitGui.py" "${INSTALLED_DIR}/"
cp -v "${REPO_DIR}/Init.py" "${INSTALLED_DIR}/"

# Copy resources if needed
if [ -d "${REPO_DIR}/resources" ]; then
  echo "Updating resources..."
  cp -rv "${REPO_DIR}/resources" "${INSTALLED_DIR}/"
fi

# Copy freecad_ai_addon module files
if [ -d "${REPO_DIR}/freecad_ai_addon" ]; then
  echo "Updating module files..."
  cp -rv "${REPO_DIR}/freecad_ai_addon" "${INSTALLED_DIR}/"
fi

echo "Update complete!"
echo "Please restart FreeCAD for the changes to take effect."
