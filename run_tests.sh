#!/bin/bash
source venv/bin/activate
python -m pytest tests/ -v --cov=freecad_ai_addon --cov-report=html
