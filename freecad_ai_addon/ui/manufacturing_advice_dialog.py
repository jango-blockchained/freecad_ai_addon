"""
Manufacturing Advice Dialog

Shows material/process recommendations and cost estimates in a simple Qt dialog.
"""

from typing import List

# Prefer FreeCAD-bundled Qt bindings: PySide (Qt4) or PySide2 (Qt5). Avoid hard-dependence on PySide6.
try:
    from PySide import QtCore as _QtCore  # type: ignore
    from PySide import QtGui as _QtGui  # type: ignore

    Qt = _QtCore.Qt  # type: ignore
    QDialog = _QtGui.QDialog  # type: ignore
    QVBoxLayout = _QtGui.QVBoxLayout  # type: ignore
    QLabel = _QtGui.QLabel  # type: ignore
    QTextEdit = _QtGui.QTextEdit  # type: ignore
    QHBoxLayout = _QtGui.QHBoxLayout  # type: ignore
    QPushButton = _QtGui.QPushButton  # type: ignore
except Exception:
    try:
        from PySide2.QtCore import Qt  # type: ignore
        from PySide2.QtWidgets import (  # type: ignore
            QDialog,
            QVBoxLayout,
            QLabel,
            QTextEdit,
            QHBoxLayout,
            QPushButton,
        )
    except Exception:
        # Last resort, some environments may provide PySide6
        from PySide6.QtCore import Qt  # type: ignore
        from PySide6.QtWidgets import (  # type: ignore
            QDialog,
            QVBoxLayout,
            QLabel,
            QTextEdit,
            QHBoxLayout,
            QPushButton,
        )

from freecad_ai_addon.advanced_features import (
    ManufacturingAdvisor,
)
from freecad_ai_addon.advanced_features.manufacturing_advisor import advice_to_dict


class ManufacturingAdviceDialog(QDialog):
    """Simple dialog to show manufacturing advice for a given object."""

    def __init__(self, object_name: str, quantity: int = 1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manufacturing Advice")
        self.resize(700, 520)

        layout = QVBoxLayout(self)

        header = QLabel(f"Advice for: <b>{object_name}</b> (qty {quantity})")
        header.setTextFormat(Qt.RichText)
        layout.addWidget(header)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text, 1)

        btn_row = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addStretch(1)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        self._load_advice(object_name, quantity)

    def _load_advice(self, object_name: str, quantity: int):
        advisor = ManufacturingAdvisor()
        advice = advisor.analyze_manufacturability(object_name, quantity=quantity)
        data = advice_to_dict(advice)

        lines: List[str] = []
        lines.append("Recommended Materials:")
        for m in data.get("recommended_materials", [])[:3]:
            lines.append(
                f"  • {m['name']} (Yield {m['yield_strength']} MPa, ${m['cost_per_kg']}/kg)"
            )

        lines.append("")
        lines.append("Recommended Processes:")
        for p in data.get("recommended_processes", [])[:3]:
            lines.append(
                f"  • {p['process'].replace('_', ' ').title()} — score {p['suitability_score']:.1f}, lead {p['lead_time_days']}d"
            )

        lines.append("")
        costs = data.get("cost_estimates", [])
        if costs:
            c0 = costs[0]
            lines.append(
                f"Cost Estimate: ${c0['total_cost']:.2f} total (${c0['cost_per_unit']:.2f}/unit)"
            )

        lines.append("")
        if data.get("dfm_recommendations"):
            lines.append("DFM Recommendations:")
            for r in data["dfm_recommendations"][:5]:
                lines.append(f"  • {r}")

        if data.get("risk_factors"):
            lines.append("")
            lines.append("Risk Factors:")
            for r in data["risk_factors"][:5]:
                lines.append(f"  • {r}")

        if data.get("timeline_estimate"):
            lines.append("")
            lines.append(f"Timeline: {data['timeline_estimate']}")

        self.text.setPlainText("\n".join(lines))
