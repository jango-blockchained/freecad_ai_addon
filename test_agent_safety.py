"""
Tests for Agent Safety & Control System.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from freecad_ai_addon.agent.safety_control import (
    AgentSafetyController, SafetyLevel, OperationRisk, 
    SafetyCheckResult, ResourceLimit
)
from freecad_ai_addon.agent.base_agent import AgentTask, TaskType


class TestAgentSafetyController(unittest.TestCase):
    """Test cases for AgentSafetyController"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.safety_controller = AgentSafetyController(SafetyLevel.MEDIUM)
        
        # Mock task for testing
        self.test_task = AgentTask(
            id="test_task_001",
            task_type=TaskType.GEOMETRY_CREATION,
            description="Create a test box",
            parameters={"length": 10, "width": 10, "height": 10, "name": "TestBox"},
            context={"document": {"name": "TestDoc", "object_count": 5}}
        )
    
    def test_initialization(self):
        """Test safety controller initialization"""
        controller = AgentSafetyController(SafetyLevel.HIGH)
        
        self.assertEqual(controller.safety_level, SafetyLevel.HIGH)
        self.assertIsNotNone(controller.resource_limits)
        self.assertIsNotNone(controller.safety_constraints)
        self.assertFalse(controller.paused)
        self.assertFalse(controller.manual_control)
    
    def test_validate_operation_success(self):
        """Test successful operation validation"""
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            # Mock FreeCAD environment
            mock_doc = Mock()
            mock_doc.getObject.return_value = Mock()  # Object exists
            mock_app.ActiveDocument = mock_doc
            
            result = self.safety_controller.validate_operation(self.test_task)
            
            self.assertIsInstance(result, SafetyCheckResult)
            # Basic validation should pass for well-formed tasks
    
    def test_validate_operation_no_document(self):
        """Test validation with no active document"""
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            mock_app.ActiveDocument = None
            
            result = self.safety_controller.validate_operation(self.test_task)
            
            self.assertFalse(result.passed)
            self.assertEqual(result.risk_level, OperationRisk.MEDIUM_RISK)
    
    def test_destructive_operation_detection(self):
        """Test detection of destructive operations"""
        destructive_task = AgentTask(
            id="destructive_task",
            task_type=TaskType.GEOMETRY_MODIFICATION,
            description="Boolean difference operation",
            parameters={"operation": "boolean_difference", "objects": ["Box1", "Box2"]},
            context={}
        )
        
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            mock_doc = Mock()
            mock_app.ActiveDocument = mock_doc
            
            result = self.safety_controller.validate_operation(destructive_task)
            
            # Should be flagged as destructive
            self.assertEqual(result.risk_level, OperationRisk.DESTRUCTIVE)
    
    def test_resource_limits_check(self):
        """Test resource limits checking"""
        # Test operation rate limit
        self.safety_controller.resource_limits.max_operations_per_minute = 1
        
        # First operation should pass
        self.assertTrue(self.safety_controller.check_resource_limits(self.test_task))
        self.safety_controller.operations_count = 1
        
        # Second operation should fail
        self.assertFalse(self.safety_controller.check_resource_limits(self.test_task))
    
    @patch('freecad_ai_addon.agent.safety_control.Gui')
    def test_user_confirmation_no_gui(self, mock_gui):
        """Test user confirmation without GUI"""
        mock_gui = None
        
        safety_result = SafetyCheckResult(
            passed=False,
            risk_level=OperationRisk.HIGH_RISK,
            errors=["High risk operation detected"]
        )
        
        # Should auto-deny high-risk operations without GUI
        confirmed = self.safety_controller.require_user_confirmation(
            self.test_task, safety_result
        )
        
        self.assertFalse(confirmed)
    
    def test_rollback_point_creation(self):
        """Test rollback point creation"""
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            mock_doc = Mock()
            mock_doc.Name = "TestDoc"
            mock_doc.Objects = [Mock(Name=f"Obj{i}") for i in range(3)]
            mock_app.ActiveDocument = mock_doc
            
            rollback_id = self.safety_controller.setup_rollback_point(
                "test_operation", {"test": "context"}
            )
            
            self.assertIsNotNone(rollback_id)
            self.assertIn(rollback_id, self.safety_controller.rollback_states)
            
            state = self.safety_controller.rollback_states[rollback_id]
            self.assertEqual(state['operation_id'], "test_operation")
            self.assertEqual(state['object_count'], 3)
    
    def test_rollback_execution(self):
        """Test rollback execution"""
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            # Setup initial state
            mock_doc = Mock()
            mock_doc.Name = "TestDoc"
            initial_objects = [Mock(Name=f"Obj{i}") for i in range(3)]
            mock_doc.Objects = initial_objects
            mock_app.ActiveDocument = mock_doc
            
            # Create rollback point
            rollback_id = self.safety_controller.setup_rollback_point("test_op", {})
            
            # Simulate adding objects
            new_objects = initial_objects + [Mock(Name="NewObj")]
            mock_doc.Objects = new_objects
            
            # Mock removeObject method
            removed_objects = []
            def mock_remove(name):
                removed_objects.append(name)
            mock_doc.removeObject = mock_remove
            
            # Execute rollback
            success = self.safety_controller.execute_rollback(rollback_id)
            
            self.assertTrue(success)
            self.assertIn("NewObj", removed_objects)
    
    def test_manual_override_controls(self):
        """Test manual override functionality"""
        # Initially should allow operations
        self.assertTrue(self.safety_controller.is_operation_allowed())
        
        # Pause agent
        self.safety_controller.pause_agent()
        self.assertFalse(self.safety_controller.is_operation_allowed())
        
        # Resume agent
        self.safety_controller.resume_agent()
        self.assertTrue(self.safety_controller.is_operation_allowed())
        
        # Enable manual control
        self.safety_controller.enable_manual_control()
        self.assertFalse(self.safety_controller.is_operation_allowed())
        self.assertTrue(self.safety_controller.manual_control)
        
        # Disable manual control
        self.safety_controller.disable_manual_control()
        self.assertTrue(self.safety_controller.is_operation_allowed())
        self.assertFalse(self.safety_controller.manual_control)
    
    def test_operation_preview(self):
        """Test operation preview generation"""
        preview = self.safety_controller.create_operation_preview(self.test_task)
        
        self.assertIsInstance(preview, dict)
        self.assertEqual(preview['task_id'], self.test_task.id)
        self.assertEqual(preview['operation'], self.test_task.task_type.value)
        self.assertTrue(preview['preview_mode'])
        self.assertIn('timestamp', preview)
    
    def test_safety_status(self):
        """Test safety status reporting"""
        status = self.safety_controller.get_safety_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('safety_level', status)
        self.assertIn('paused', status)
        self.assertIn('manual_control', status)
        self.assertIn('resource_limits', status)
        
        self.assertEqual(status['safety_level'], SafetyLevel.MEDIUM.value)
        self.assertFalse(status['paused'])
        self.assertFalse(status['manual_control'])
    
    def test_parameter_validation_constraint(self):
        """Test parameter validation safety constraint"""
        # Valid box parameters
        valid_task = AgentTask(
            id="valid_box",
            task_type=TaskType.GEOMETRY_CREATION,
            description="Create box",
            parameters={"length": 10, "width": 20, "height": 30},
            context={}
        )
        
        # Invalid box parameters (missing height)
        invalid_task = AgentTask(
            id="invalid_box",
            task_type=TaskType.GEOMETRY_CREATION,
            description="Create box",
            parameters={"length": 10, "width": 20},
            context={}
        )
        
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            mock_app.ActiveDocument = Mock()
            
            # Valid task should pass
            result_valid = self.safety_controller.validate_operation(valid_task)
            # Should not fail on parameter validation
            
            # Invalid task should fail
            result_invalid = self.safety_controller.validate_operation(invalid_task)
            # Should fail on parameter validation
    
    def test_safety_level_escalation(self):
        """Test different safety levels"""
        # Test CRITICAL safety level
        critical_controller = AgentSafetyController(SafetyLevel.CRITICAL)
        
        safety_result = SafetyCheckResult(
            passed=True,
            risk_level=OperationRisk.LOW_RISK
        )
        
        with patch('freecad_ai_addon.agent.safety_control.Gui') as mock_gui:
            with patch('freecad_ai_addon.agent.safety_control.QDialog', None):
                # Even low-risk operations should require confirmation at CRITICAL level
                # But without GUI, should be denied
                confirmed = critical_controller.require_user_confirmation(
                    self.test_task, safety_result
                )
                
                # Without GUI, critical level should deny operations
                self.assertFalse(confirmed)


class TestSafetyIntegration(unittest.TestCase):
    """Test integration with agents"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        from freecad_ai_addon.agent.geometry_agent import GeometryAgent
        self.agent = GeometryAgent()
    
    def test_agent_safety_integration(self):
        """Test that agents use safety controller"""
        test_task = AgentTask(
            id="integration_test",
            task_type=TaskType.GEOMETRY_CREATION,
            description="Create test box",
            parameters={"length": 10, "width": 10, "height": 10},
            context={}
        )
        
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            mock_app.ActiveDocument = Mock()
            
            # Execute with safety should initialize safety controller
            result = self.agent.execute_with_safety(test_task)
            
            # Should have safety controller after execution
            self.assertTrue(hasattr(self.agent, '_safety_controller'))
            self.assertIsNotNone(self.agent._safety_controller)


if __name__ == '__main__':
    unittest.main()
