# FreeCAD AI Addon User Manual

## Introduction

- Overview of features
- Installation instructions

## Getting Started

- Basic usage
- Example workflows

## Advanced Features

- Agent mode
- Provider management

### Manufacturing Advisor

The Manufacturing Advisor helps select materials and processes, estimates cost, and suggests DFM improvements.

GUI usage:

- Switch to the "AI Assistant" workbench.
- Open: AI Assistant → Manufacturing Advice.
- Optionally select a part in the tree; enter your target quantity.
- Review:
	- Recommended materials and processes with scores and lead times
	- Cost estimate and breakdown by category
	- DFM recommendations, risks, and suggested timeline

Python API (headless/mock mode):

```python
from freecad_ai_addon.advanced_features import ManufacturingAdvisor

advisor = ManufacturingAdvisor(mock_mode=True)
advice = advisor.analyze_manufacturability(object_name="Bracket", quantity=50)
print(advice.summary)
```

## Troubleshooting

- Common issues and solutions

## Best Practices

- AI interaction tips
- FreeCAD workflow recommendations

## FAQ

- Frequently asked questions
