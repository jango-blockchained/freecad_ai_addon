#!/usr/bin/env python3
"""
Debug script to isolate the hanging issue in test_autonomous_task_execution_simple
"""

import sys
import time
from unittest.mock import Mock, patch

print("Starting debug script...")

# Add the current directory to path
sys.path.insert(0, "/home/jango/Git/freecad_ai_addon")

print("Importing modules...")

try:
    from freecad_ai_addon.agent.agent_framework import AIAgentFramework

    print("✓ Imported AIAgentFramework")
except Exception as e:
    print(f"✗ Failed to import AIAgentFramework: {e}")
    sys.exit(1)

try:
    from freecad_ai_addon.agent.safety_control import SafetyLevel

    print("✓ Imported SafetyLevel")
except Exception as e:
    print(f"✗ Failed to import SafetyLevel: {e}")

try:
    from freecad_ai_addon.agent.base_agent import TaskType

    print("✓ Imported TaskType")
except Exception as e:
    print(f"✗ Failed to import TaskType: {e}")

print("\nInitializing framework...")
try:
    framework = AIAgentFramework()
    print("✓ Framework initialized")
except Exception as e:
    print(f"✗ Framework initialization failed: {e}")
    sys.exit(1)

print("\nSetting up mocks...")
with patch("freecad_ai_addon.agent.safety_control.App") as mock_app:
    # Setup FreeCAD mock
    mock_doc = Mock()
    mock_doc.Objects = []
    mock_doc.recompute = Mock()
    mock_app.ActiveDocument = mock_doc

    # Mock geometry creation
    mock_box = Mock()
    mock_box.Name = "TestBox"

    def mock_add_object(type_name, name):
        if type_name == "Part::Box":
            return mock_box
        return Mock()

    mock_doc.addObject = mock_add_object

    print("✓ Mocks set up")

    print("\nCalling execute_autonomous_task...")
    print("This is where the hang likely occurs...")

    # Add a timeout mechanism
    import signal

    def timeout_handler(signum, frame):
        print("\n✗ TIMEOUT: execute_autonomous_task is hanging!")
        raise TimeoutError("Function call timed out")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout

    try:
        result = framework.execute_autonomous_task(
            "Create a 10x20x30mm box", context={"test": True}
        )
        signal.alarm(0)  # Cancel the alarm
        print("✓ execute_autonomous_task completed")
        print(f"Result: {result}")
    except TimeoutError:
        print("✗ Function timed out - this is the source of the hang!")
    except Exception as e:
        signal.alarm(0)  # Cancel the alarm
        print(f"✗ Exception in execute_autonomous_task: {e}")
        import traceback

        traceback.print_exc()

print("\nDebug script completed.")
