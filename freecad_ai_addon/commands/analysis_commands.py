"""Analysis & validation related FreeCAD commands (Rule Checker, Optimization, Simulation).

Each command is defensive: it works headless (prints/logs) and in GUI
(uses simple dialogs if Qt available). This keeps unit tests lightweight
while providing immediate user value inside FreeCAD.
"""
from __future__ import annotations

try:  # FreeCAD optional
    import FreeCADGui as Gui  # type: ignore
except ImportError:  # pragma: no cover
    Gui = None  # type: ignore

from freecad_ai_addon.utils.logging import get_logger
from freecad_ai_addon.advanced_features import (
    DesignRuleChecker,
    DesignOptimizationEngine,
    SimulationAssistant,
    OptimizationGoal,
)

logger = get_logger("analysis_commands")

# ---- Helper dialog abstraction ------------------------------------------------


def _show_text_dialog(title: str, text: str):  # pragma: no cover - GUI only
    if not Gui:
        return
    try:
        from PySide2.QtWidgets import QMessageBox  # type: ignore

        QMessageBox.information(None, title, text[:6000])
    except Exception:  # noqa: BLE001
        pass


def _selected_name():
    try:
        if Gui and hasattr(Gui, "Selection"):
            sel = Gui.Selection.getSelection()
            if sel:
                return getattr(sel[0], "Name", None)
    except Exception:  # noqa: BLE001
        return None
    return None


# ---- Rule Checker Command ----------------------------------------------------
class RunDesignRuleCheckCommand:
    def GetResources(self):
        return {
            "Pixmap": "ai_rule_check.svg",
            "MenuText": "Run Design Rule Check",
            "ToolTip": "Validate selected object against design & manufacturing rules",
        }

    def IsActive(self):  # always active for MVP
        return True

    def Activated(self):
        target = _selected_name() or "ActivePart"
        checker = DesignRuleChecker()
        report = checker.check_design(target)
        lines = [f"Design Rule Report for {target}"]
        lines.append(
            f"Score: {report.overall_score:.1f}/100  Violations: {len(report.violations_found)}"
        )
        for v in report.violations_found[:5]:
            lines.append(f" - {v.rule.name}: {v.description} (sev={v.severity.value})")
        if not report.violations_found:
            lines.append("No violations detected (mock or clean)")
        text = "\n".join(lines)
        if Gui:
            _show_text_dialog("Design Rule Report", text)
        else:
            print(text)


# ---- Optimization Suggestions Command ----------------------------------------
class ShowOptimizationSuggestionsCommand:
    def GetResources(self):
        return {
            "Pixmap": "ai_optimization.svg",
            "MenuText": "Show Optimization Suggestions",
            "ToolTip": "Analyze object for optimization opportunities (mock/headless supported)",
        }

    def IsActive(self):
        return True

    def Activated(self):
        target = _selected_name() or "ActivePart"
        engine = DesignOptimizationEngine()
        opps = engine.suggest_optimization_opportunities(target)
        lines = [f"Optimization Opportunities for {target}"]
        for k, v in opps.items():
            if isinstance(v, dict):
                headline = (
                    v.get("potential_reduction")
                    or v.get("potential_improvement")
                    or v.get("suitability")
                )
                if headline:
                    lines.append(f" - {k.replace('_', ' ').title()}: {headline}")
        text = "\n".join(lines)
        if Gui:
            _show_text_dialog("Optimization Suggestions", text)
        else:
            print(text)


# ---- Simulation Setup Recommendation Command ---------------------------------
class RecommendSimulationSetupCommand:
    def GetResources(self):
        return {
            "Pixmap": "ai_simulation.svg",
            "MenuText": "Recommend Simulation Setup",
            "ToolTip": "Generate simulation setup recommendation (structural default)",
        }

    def IsActive(self):
        return True

    def Activated(self):
        target = _selected_name() or "ActivePart"
        assistant = SimulationAssistant()
        rec = assistant.recommend_simulation_setup(target, "stress analysis")
        lines = [f"Simulation Setup for {target}"]
        lines.append(f"Type: {rec.setup.simulation_type.value}")
        lines.append(f"Material: {rec.setup.material.name}")
        lines.append(
            f"Mesh: {rec.setup.mesh_settings.quality.value} size={rec.setup.mesh_settings.element_size} mm"
        )
        lines.append(
            f"Boundary conditions: {len(rec.setup.load_cases[0].boundary_conditions)}"
        )
        lines.append(f"Confidence: {rec.confidence:.2f}")
        text = "\n".join(lines)
        if Gui:
            _show_text_dialog("Simulation Recommendation", text)
        else:
            print(text)


if Gui and hasattr(Gui, "addCommand"):
    Gui.addCommand("AI_RunDesignRuleCheck", RunDesignRuleCheckCommand())
    Gui.addCommand(
        "AI_ShowOptimizationSuggestions", ShowOptimizationSuggestionsCommand()
    )
    Gui.addCommand("AI_RecommendSimulationSetup", RecommendSimulationSetupCommand())

__all__ = [
    "RunDesignRuleCheckCommand",
    "ShowOptimizationSuggestionsCommand",
    "RecommendSimulationSetupCommand",
]
