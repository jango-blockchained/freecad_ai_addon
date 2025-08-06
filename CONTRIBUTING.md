# Contributing to FreeCAD AI Addon

Thank you for your interest in contributing to the FreeCAD AI Addon! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. **Check existing issues** - Search the issue tracker first
2. **Create a detailed report** - Include:
   - FreeCAD version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Log files (located in `~/.FreeCAD/logs/ai_addon/`)

### Suggesting Features

1. **Search existing suggestions** - Check if it's already been proposed
2. **Create a feature request** - Include:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach
   - Mock-ups or examples if helpful

### Contributing Code

#### Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/freecad-ai-addon.git
   cd freecad-ai-addon
   ```
3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Coding Standards

- **Python Style**: Follow PEP 8
- **Line Length**: Maximum 79 characters
- **Imports**: Group and sort imports properly
- **Documentation**: Use docstrings for all public functions and classes
- **Type Hints**: Use type hints where appropriate

#### Code Quality Tools

Run these tools before submitting:

```bash
# Format code
black freecad_ai_addon/

# Check style
flake8 freecad_ai_addon/

# Type checking
mypy freecad_ai_addon/

# Run tests
pytest tests/
```

#### Testing

- **Unit Tests**: Required for all new functionality
- **Integration Tests**: Required for FreeCAD integration features
- **Test Coverage**: Maintain > 80% coverage
- **Test Location**: Place tests in `tests/` directory

Example test structure:
```python
def test_feature_name():
    """Test description"""
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result == expected_value
```

#### Documentation

- **Code Comments**: Explain complex logic
- **Docstrings**: Document public APIs
- **User Documentation**: Update README.md and docs/ as needed
- **API Documentation**: Update docstrings for public interfaces

### Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add conversation history export"
   ```

2. **Use conventional commits**:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `test:` - Adding tests
   - `refactor:` - Code refactoring
   - `style:` - Code style changes
   - `perf:` - Performance improvements

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request**:
   - Provide clear title and description
   - Reference related issues
   - Include screenshots for UI changes
   - Ensure all checks pass

### Pull Request Guidelines

- **One feature per PR** - Keep changes focused
- **Clear description** - Explain what and why
- **Tests included** - All new code should have tests
- **Documentation updated** - Update relevant docs
- **No merge commits** - Rebase instead of merging
- **Linear history** - Squash commits if needed

## Project Structure

```
freecad_ai_addon/
├── core/                   # Core functionality
│   ├── mcp_client/        # MCP integration
│   ├── provider_manager/   # AI provider management
│   └── agent_framework/    # Agent implementation
├── ui/                     # User interface
│   ├── conversation_widget/
│   ├── provider_settings/
│   └── agent_control_panel/
├── integration/            # FreeCAD integration
│   ├── workbench.py       # Main workbench
│   ├── context_providers/ # Context extraction
│   └── action_executors/  # Action execution
├── utils/                 # Utilities
│   ├── logging.py         # Logging system
│   ├── config.py          # Configuration
│   ├── security.py        # Security utilities
│   └── analytics.py       # Analytics
├── resources/             # Resources
│   ├── icons/            # UI icons
│   ├── templates/        # Code templates
│   └── docs/             # Documentation
└── tests/                # Test suite
```

## Development Phases

The project is organized into phases (see `taskplan.md`):

1. **Phase 1**: Foundation & Setup
2. **Phase 2**: MCP Integration
3. **Phase 3**: Provider Management
4. **Phase 4**: Conversation Widget
5. **Phase 5**: Agent Mode
6. **Phase 6**: Advanced Features
7. **Phase 7**: Testing & QA
8. **Phase 8**: Documentation & Deployment

Choose tasks from the current phase or upcoming phases.

## Areas for Contribution

### High Priority
- MCP client implementation
- Provider management system
- Conversation widget development
- FreeCAD context extraction
- Security and encryption

### Medium Priority
- Agent framework
- Advanced UI features
- Performance optimization
- Additional AI providers
- Testing improvements

### Documentation
- User guides and tutorials
- API documentation
- Video demonstrations
- Translation support

## Getting Help

- **Discord**: [FreeCAD AI Addon Server](https://discord.gg/freecad-ai)
- **Forum**: [FreeCAD Forum AI Thread](https://forum.freecad.org)
- **GitHub Discussions**: Use for questions and ideas
- **GitHub Issues**: Use for bugs and feature requests

## Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Acknowledged in the about dialog
- Invited to maintainer discussions (for significant contributors)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the FreeCAD AI Addon! 🚀
