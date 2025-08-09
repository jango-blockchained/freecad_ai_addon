#!/usr/bin/env python3
"""
Test script to verify AI Workbench functionality in FreeCAD GUI mode.

This script can be run from within FreeCAD GUI to check if the addon is working correctly.
Copy and paste the content into FreeCAD's Python console or run it as a macro.
"""


def test_ai_workbench():
    """Basic diagnostic that is a no-op outside FreeCAD GUI."""
    print("=== AI Workbench Diagnostic Test ===")

    try:
        import FreeCADGui as Gui  # type: ignore
    except ImportError:
        # Not running inside FreeCAD GUI; nothing to test
        print("GUI modules not available; skipping diagnostic.")
        return True

    print("✅ FreeCAD GUI module imported")
    has_gui = hasattr(Gui, "Workbench") and hasattr(Gui, "listWorkbenches")
    print(f"GUI Mode: {'✅ Yes' if has_gui else '❌ No (Console mode)'}")

    if has_gui:
        print("\nAvailable workbenches:")
        try:
            workbenches = Gui.listWorkbenches()
        except (AttributeError, RuntimeError, ValueError) as exc:
            print(f"❌ Error listing workbenches: {exc}")
            workbenches = {}

        for name in sorted(workbenches.keys()):
            try:
                wb = Gui.getWorkbench(name)
                menu_text = getattr(wb, "MenuText", name)
                print(f"  {name}: {menu_text}")
            except (AttributeError, RuntimeError, ValueError, TypeError):
                print(f"  {name}: (unable to get details)")

    # Test importing our addon
    try:
        import InitGui  # type: ignore
    except ImportError as exc:
        print(f"❌ Failed to import InitGui: {exc}")
        return False

    print("✅ InitGui imported successfully")

    if not hasattr(InitGui, "AIWorkbench"):
        print("❌ AIWorkbench class not found in InitGui")
        return False

    print("✅ AIWorkbench class found")
    try:
        wb = InitGui.AIWorkbench()
    except (TypeError, RuntimeError, ValueError) as exc:
        print(f"❌ AIWorkbench instantiation failed: {exc}")
        return False

    print(f"✅ AIWorkbench instantiated: {getattr(wb, 'MenuText', 'AI Assistant')}")
    if hasattr(wb, "_set_icon_path"):
        try:
            wb.Initialize()
            print("✅ Workbench initialized successfully")
        except (RuntimeError, AttributeError, ValueError) as exc:
            print(f"⚠️  Workbench initialization raised: {exc}")
    else:
        print("ℹ️  Using fallback workbench (basic)")

    print("\n=== Diagnostic Complete ===")
    return True


if __name__ == "__main__":
    test_ai_workbench()
