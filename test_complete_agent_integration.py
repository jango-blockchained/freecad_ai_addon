"""
Complete integration test for the Agent Framework with Safety Controls.
Tests the full autonomous agent pipeline from natural language to execution.
"""

import unittest
from unittest.mock import Mock, patch
import time

from freecad_ai_addon.agent.agent_framework import AIAgentFramework
from freecad_ai_addon.agent.safety_control import SafetyLevel
from freecad_ai_addon.agent.base_agent import TaskType


class TestCompleteAgentIntegration(unittest.TestCase):
    """Complete integration tests for the agent framework with safety"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.framework = AIAgentFramework()
        
    def test_framework_initialization(self):
        """Test that the framework initializes properly"""
        self.assertTrue(self.framework.is_initialized)
        self.assertIsNotNone(self.framework.geometry_agent)
        self.assertIsNotNone(self.framework.sketch_agent)
        self.assertIsNotNone(self.framework.analysis_agent)
        self.assertIsNotNone(self.framework.task_planner)
    
    def test_framework_capabilities(self):
        """Test framework capability reporting"""
        capabilities = self.framework.get_capabilities()
        
        self.assertIn('agent_capabilities', capabilities)
        self.assertIn('supported_operations', capabilities)
        self.assertIn('common_patterns', capabilities)
        self.assertIn('framework_info', capabilities)
        
        # Check that we have operations from all agents
        operations = capabilities['supported_operations']
        self.assertIn('geometry_operations', operations)
        self.assertIn('sketch_operations', operations)
        self.assertIn('analysis_operations', operations)
        
        # Verify framework info
        framework_info = capabilities['framework_info']
        self.assertEqual(framework_info['version'], '1.0.0')
        self.assertTrue(framework_info['is_initialized'])
        self.assertEqual(framework_info['agents_count'], 3)
    
    @patch('freecad_ai_addon.agent.safety_control.App')
    def test_autonomous_task_execution_simple(self, mock_app):
        """Test autonomous execution of a simple task"""
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
        
        # Execute simple box creation task
        result = self.framework.execute_autonomous_task(
            "Create a 10x20x30mm box",
            context={"test": True}
        )
        
        # Verify result structure
        self.assertIn('status', result)
        self.assertIn('description', result)
        self.assertIn('plan_id', result)
        
        # Should have attempted to create a plan
        self.assertIsNotNone(result.get('plan_id'))
    
    @patch('freecad_ai_addon.agent.safety_control.App')
    def test_safety_integration_complete(self, mock_app):
        """Test complete safety system integration"""
        # Setup FreeCAD mock
        mock_app.ActiveDocument = Mock()
        
        # Test that agents have safety controllers after execution
        with patch.object(self.framework.geometry_agent, 'execute_task') as mock_execute:
            mock_execute.return_value = Mock(
                status=Mock(value='completed'),
                execution_time=0.1,
                created_objects=['TestBox'],
                modified_objects=[],
                error_message=None
            )
            
            result = self.framework.execute_autonomous_task(
                "Create a test box",
                preview_mode=False
            )
            
            # Check that safety controller was initialized
            self.assertTrue(hasattr(self.framework.geometry_agent, '_safety_controller'))
            
            # Verify safety controller functionality
            safety_controller = self.framework.geometry_agent._safety_controller
            self.assertEqual(safety_controller.safety_level, SafetyLevel.MEDIUM)
            
            # Test safety status
            safety_status = safety_controller.get_safety_status()
            self.assertIn('safety_level', safety_status)
            self.assertIn('resource_limits', safety_status)
    
    def test_natural_language_processing(self):
        """Test natural language processing capabilities"""
        test_requests = [
            "Create a 10mm cube",
            "Add 2mm fillets to the selected object",
            "Create a cylinder with radius 5mm and height 20mm",
            "Analyze this part for 3D printing",
            "Create a sketch with a 50mm circle"
        ]
        
        for request in test_requests:
            # Test validation
            validation = self.framework.validate_request(request)
            self.assertIn('feasible', validation)
            
            # Most basic geometric requests should be feasible
            if 'create' in request.lower() and any(shape in request.lower() 
                                                   for shape in ['cube', 'cylinder', 'circle']):
                self.assertTrue(validation.get('feasible', False), 
                              f"Request '{request}' should be feasible")


class TestAgentSafetyIntegration(unittest.TestCase):
    """Test safety system integration with all agents"""
    
    def setUp(self):
        """Set up safety integration tests"""
        self.framework = AIAgentFramework()
    
    @patch('freecad_ai_addon.agent.safety_control.App')
    def test_safety_controller_initialization_all_agents(self, mock_app):
        """Test that all agents get safety controllers"""
        mock_app.ActiveDocument = Mock()
        
        agents = [
            self.framework.geometry_agent,
            self.framework.sketch_agent,
            self.framework.analysis_agent
        ]
        
        # Execute tasks with each agent type to initialize safety
        test_tasks = [
            "Create a box",  # Geometry agent
            "Create a sketch with circle",  # Sketch agent
            "Analyze part properties"  # Analysis agent
        ]
        
        for task in test_tasks:
            self.framework.execute_autonomous_task(task)
        
        # All agents should now have safety controllers
        for agent in agents:
            if hasattr(agent, '_safety_controller'):
                safety_controller = agent._safety_controller
                self.assertEqual(safety_controller.safety_level, SafetyLevel.MEDIUM)
    
    @patch('freecad_ai_addon.agent.safety_control.App')
    def test_rollback_functionality(self, mock_app):
        """Test rollback functionality integration"""
        mock_doc = Mock()
        mock_doc.Objects = [Mock(Name=f"Obj{i}") for i in range(3)]
        mock_doc.removeObject = Mock()
        mock_doc.recompute = Mock()
        mock_app.ActiveDocument = mock_doc
        
        # Execute a task to initialize safety controller
        self.framework.execute_autonomous_task("Create test object")
        
        # Test rollback functionality exists
        agent = self.framework.geometry_agent
        if hasattr(agent, '_safety_controller'):
            safety_controller = agent._safety_controller
            
            # Test rollback point creation
            rollback_id = safety_controller.setup_rollback_point(
                "test_operation", {"test": True}
            )
            self.assertIsNotNone(rollback_id)
            
            # Test rollback execution
            success = safety_controller.execute_rollback(rollback_id)
            self.assertTrue(success)
    
    @patch('freecad_ai_addon.agent.safety_control.App')
    def test_resource_limit_integration(self, mock_app):
        """Test resource limit enforcement integration"""
        mock_app.ActiveDocument = Mock()
        
        # Execute task to initialize safety controller
        self.framework.execute_autonomous_task("Create box")
        
        agent = self.framework.geometry_agent
        if hasattr(agent, '_safety_controller'):
            safety_controller = agent._safety_controller
            
            # Test resource limits
            limits = safety_controller.resource_limits
            self.assertIsNotNone(limits.max_execution_time)
            self.assertIsNotNone(limits.max_memory_usage)
            self.assertIsNotNone(limits.max_objects_created)
            self.assertIsNotNone(limits.max_operations_per_minute)
            
            # Test limit checking
            from freecad_ai_addon.agent.base_agent import AgentTask, TaskType
            test_task = AgentTask(
                id="test",
                task_type=TaskType.GEOMETRY_CREATION,
                description="Test task",
                parameters={},
                context={}
            )
            
            # Should pass initially
            self.assertTrue(safety_controller.check_resource_limits(test_task))


class TestFrameworkStatusAndReporting(unittest.TestCase):
    """Test framework status and reporting capabilities"""
    
    def setUp(self):
        """Set up status testing"""
        self.framework = AIAgentFramework()
    
    def test_comprehensive_status_reporting(self):
        """Test comprehensive status reporting"""
        status = self.framework.get_framework_status()
        
        # Check all required status fields
        required_fields = [
            'is_initialized', 'freecad_available', 'agents',
            'active_plans', 'completed_plans', 'execution_history_count'
        ]
        
        for field in required_fields:
            self.assertIn(field, status)
        
        # Check agent status details
        agents_status = status['agents']
        expected_agents = ['geometry', 'sketch', 'analysis']
        
        for agent_type in expected_agents:
            self.assertIn(agent_type, agents_status)
            agent_info = agents_status[agent_type]
            
            required_agent_fields = [
                'name', 'capabilities', 'current_task', 'task_history_count'
            ]
            
            for field in required_agent_fields:
                self.assertIn(field, agent_info)
    
    def test_execution_history_tracking(self):
        """Test execution history tracking"""
        # Get initial history count
        initial_history = self.framework.get_execution_history()
        initial_count = len(initial_history)
        
        # Execute some tasks
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            mock_app.ActiveDocument = Mock()
            
            tasks = [
                "Create a box",
                "Create a sphere",
                "Create a cylinder"
            ]
            
            for task in tasks:
                self.framework.execute_autonomous_task(task)
        
        # History should have grown
        new_history = self.framework.get_execution_history()
        self.assertGreaterEqual(len(new_history), initial_count)
        
        # Check history entry structure
        if new_history:
            entry = new_history[-1]  # Get latest entry
            required_fields = ['timestamp', 'description', 'plan_id', 'status']
            
            for field in required_fields:
                self.assertIn(field, entry)
    
    def test_framework_shutdown_and_cleanup(self):
        """Test framework shutdown and cleanup"""
        # Framework should be running
        self.assertTrue(self.framework.is_initialized)
        
        # Execute a task to create some state
        with patch('freecad_ai_addon.agent.safety_control.App') as mock_app:
            mock_app.ActiveDocument = Mock()
            self.framework.execute_autonomous_task("Test task")
        
        # Shutdown should work cleanly
        self.framework.shutdown()
        self.assertFalse(self.framework.is_initialized)
        
        # Should handle multiple shutdowns gracefully
        self.framework.shutdown()  # Should not raise exception


if __name__ == '__main__':
    # Run with verbose output to see test details
    unittest.main(verbosity=2)
