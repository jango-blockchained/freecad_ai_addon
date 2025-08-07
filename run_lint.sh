#!/bin/bash
source venv/bin/activate
echo "Running Black..."
black freecad_ai_addon/
echo "Running Flake8..."
flake8 freecad_ai_addon/
echo "Running MyPy..."
mypy freecad_ai_addon/ --ignore-missing-imports
