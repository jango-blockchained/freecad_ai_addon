"""
Test script for the AI Agent Framework.
Demonstrates basic functionality and usage patterns.
"""

import sys
import os

from freecad_ai_addon.agent import AIAgentFramework

# Add the parent directory to the path so we can import the agent framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_agent_framework():
    """Test the AI Agent Framework functionality"""
    print("=== FreeCAD AI Agent Framework Test ===\n")
    
    # Initialize the framework
    print("1. Initializing AI Agent Framework...")
    framework = AIAgentFramework()
    print("✓ Framework initialized successfully")
    
    # Get capabilities
    print("\n2. Getting framework capabilities...")
    capabilities = framework.get_capabilities()
    print(f"✓ Framework has {len(capabilities['supported_operations'])} operation categories")
    print(f"✓ {capabilities['framework_info']['agents_count']} agents registered")
    
    # Print available operations
    print("\n3. Available Operations:")
    for category, operations in capabilities['supported_operations'].items():
        print(f"   {category.title()}: {len(operations)} operations")
        for op in operations[:3]:  # Show first 3 operations
            print(f"     - {op}")
        if len(operations) > 3:
            print(f"     ... and {len(operations) - 3} more")
    
    # Test request validation
    print("\n4. Testing request validation...")
    test_requests = [
        "Create a 10x20x30mm box",
        "Add 2mm fillets to selected object",
        "Analyze this part for 3D printing",
        "Create an impossible quantum geometry"  # This should fail
    ]
    
    for request in test_requests:
        print(f"\n   Request: '{request}'")
        validation = framework.validate_request(request)
        if validation['feasible']:
            print(f"   ✓ Feasible - {validation['task_count']} tasks planned")
        else:
            print(f"   ✗ Not feasible - {validation['reason']}")
    
    # Test preview mode execution
    print("\n5. Testing preview mode execution...")
    preview_request = "Create a 25mm cube and add 3mm fillets"
    print(f"   Request: '{preview_request}'")
    
    preview_result = framework.execute_autonomous_task(
        preview_request, 
        preview_mode=True
    )
    
    if preview_result['status'] == 'preview':
        print(f"   ✓ Preview generated - {preview_result['task_count']} tasks")
        for i, task in enumerate(preview_result['tasks_preview'], 1):
            print(f"     Task {i}: {task['description']}")
    else:
        print("   ✗ Preview failed")
    
    # Test framework status
    print("\n6. Framework status:")
    status = framework.get_framework_status()
    print(f"   Initialized: {status['is_initialized']}")
    print(f"   FreeCAD Available: {status['freecad_available']}")
    print(f"   Active Plans: {status['active_plans']}")
    print(f"   Completed Plans: {status['completed_plans']}")
    
    # Shutdown
    print("\n7. Shutting down framework...")
    framework.shutdown()
    print("✓ Framework shutdown complete")
    
    print("\n=== Test completed successfully! ===")


def demo_natural_language_examples():
    """Demonstrate natural language processing capabilities"""
    print("\n=== Natural Language Processing Demo ===\n")
    
    framework = AIAgentFramework()
    
    examples = [
        "Create a box that is 50mm long, 30mm wide, and 20mm high",
        "Make a cylinder with radius 15mm and height 40mm",
        "Add 5mm fillets to all edges of the selected object",
        "Analyze the selected part for 3D printing compatibility",
        "Create a sketch with a 25mm diameter circle",
        "Perform a boolean union on the two selected objects",
        "Check if these two parts intersect with each other"
    ]
    
    print("Processing natural language requests:\n")
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. Request: '{example}'")
        
        # Validate the request
        validation = framework.validate_request(example)
        
        if validation['feasible']:
            print(f"   ✓ Parsed into {validation['task_count']} tasks:")
            for task in validation['plan_preview']:
                print(f"     - {task['description']}")
        else:
            print(f"   ✗ Could not parse: {validation['reason']}")
        
        print()  # Empty line for readability
    
    framework.shutdown()


if __name__ == "__main__":
    # Run tests
    test_agent_framework()
    demo_natural_language_examples()
    
    print("\n" + "="*60)
    print("AI Agent Framework is ready for integration!")
    print("="*60)
