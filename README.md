# FreeCAD AI Addon

A comprehensive AI-powered design assistant for FreeCAD that integrates AI capabilities through Model Context Protocol (MCP), providing users with an intelligent conversation interface and autonomous agent capabilities for CAD operations.

## Features

🤖 **AI Integration**: Connect to multiple AI providers (OpenAI, Anthropic, local models) through MCP
💬 **Conversation Interface**: Modern chat widget integrated directly into FreeCAD
🔐 **Secure Provider Management**: Encrypted storage and management of API keys
🎯 **Agent Mode**: Autonomous AI agent for complex CAD operations
📐 **FreeCAD Context Awareness**: Deep integration with FreeCAD's state and objects
🎨 **Modern UI**: Clean, responsive interface built with PySide6

## Current Development Status

🚧 **The FreeCAD AI Addon is currently in active development** 🚧

### ✅ Completed (Phase 1 & 2)

**Phase 1: Foundation & Setup**
- ✅ Complete FreeCAD addon directory structure
- ✅ Python package structure with proper modules
- ✅ FreeCAD integration files (`InitGui.py`, `Init.py`, `package.xml`)
- ✅ Basic AI Workbench implementation
- ✅ Centralized logging and configuration system
- ✅ Development environment setup (requirements, tests, docs)
- ✅ Comprehensive project documentation

**Phase 2: MCP Integration Layer**
- ✅ **MCP Client Manager**: Full implementation with support for stdio, HTTP, and SSE transports
- ✅ **AI Provider Manager**: Complete abstraction layer supporting OpenAI, Anthropic, and Ollama
- ✅ **FreeCAD Context Provider**: Deep integration extracting document structure, geometry, sketches, and selections
- ✅ **Security Framework**: Encrypted credential storage and secure API key management

### 🔧 Current Capabilities

The addon now includes a sophisticated foundation with:

1. **Multi-Provider AI Support**:
   - OpenAI (GPT-3.5, GPT-4, GPT-4 Turbo)
   - Anthropic (Claude 3 Haiku, Sonnet, Opus)
   - Local models via Ollama
   - Easy addition of new providers

2. **Model Context Protocol Integration**:
   - Full MCP client implementation
   - Support for multiple transport methods
   - Tool and resource discovery
   - Session management with reconnection

3. **FreeCAD Deep Integration**:
   - Complete document state extraction
   - Geometric analysis and measurements
   - Sketch constraint information
   - Selection and visibility tracking
   - Workbench and view state awareness

4. **Enterprise-Grade Security**:
   - Encrypted API key storage
   - Secure configuration management
   - No telemetry without consent
   - Local-first data handling

### 🎯 Next Steps (Phase 3-4)

**Phase 3: Provider Management System** (In Progress)
- Secure credential storage UI
- Provider configuration dialogs
- Connection testing and validation
- Usage statistics and monitoring

**Phase 4: Conversation Widget** (Coming Soon)
- Modern PySide6 chat interface
- Markdown rendering with code highlighting
- Context-aware conversations
- FreeCAD integration buttons

## Installation

### From FreeCAD Addon Manager (Recommended)
1. Open FreeCAD
2. Go to Tools → Addon Manager
3. Search for "FreeCAD AI Addon"
4. Click Install

### Manual Installation
1. Download the addon from the [releases page](https://github.com/username/freecad-ai-addon/releases)
2. Extract to your FreeCAD addon directory:
   - **Linux**: `~/.FreeCAD/Mod/freecad_ai_addon/`
   - **Windows**: `%APPDATA%\FreeCAD\Mod\freecad_ai_addon\`
   - **macOS**: `~/Library/Application Support/FreeCAD/Mod/freecad_ai_addon/`
3. Restart FreeCAD

## Requirements

- **FreeCAD**: Version 0.20 or higher
- **Python**: 3.8 or higher (provided by FreeCAD)
- **Internet Connection**: Required for AI provider access

## Quick Start

1. **Install the addon** using one of the methods above
2. **Restart FreeCAD** to load the addon
3. **Switch to AI Assistant workbench** from the workbench dropdown
4. **Configure AI provider**:
   - Click the Settings button in the AI toolbar
   - Add your API keys for desired AI providers
   - Test the connection
5. **Start chatting**:
   - Click the Chat button to open the conversation widget
   - Ask questions about your design or request assistance
6. **Try Agent Mode**:
   - Enable Agent Mode for autonomous operations
   - Describe what you want to achieve
   - Review and approve suggested actions

## Configuration

The addon stores configuration in your FreeCAD user directory:
- **Linux**: `~/.FreeCAD/ai_addon/`
- **Windows**: `%APPDATA%\FreeCAD\ai_addon\`
- **macOS**: `~/Library/Application Support/FreeCAD/ai_addon/`

### Supported AI Providers

- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude 3 (Haiku, Sonnet, Opus)
- **Local Models**: Ollama, custom MCP servers

## Usage Examples

### Basic Conversation
```
User: "How do I create a chamfer on this edge?"
AI: "To create a chamfer on the selected edge, you can use the Part Design Chamfer tool..."
```

### Agent Mode
```
User: "Create a 50mm cube with 5mm chamfers on all edges"
AI: "I'll create that for you. Let me:
1. Create a 50mm cube
2. Apply 5mm chamfers to all 12 edges
[Execute] [Preview] [Cancel]"
```

### Context-Aware Assistance
```
User: "Optimize this part for 3D printing"
AI: "I can see you have a complex geometry with overhangs. Here are my recommendations:
- Add support structures at these locations...
- Adjust the orientation for better surface finish...
- Consider splitting into multiple parts..."
```

## Development

### Setting up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/username/freecad-ai-addon.git
   cd freecad-ai-addon
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests**:
   ```bash
   pytest tests/
   ```

### Project Structure

```
freecad_ai_addon/
├── core/               # Core engine (MCP, providers, agents)
├── ui/                 # User interface components
├── integration/        # FreeCAD integration (workbench, commands)
├── utils/              # Utilities (logging, config, security)
└── resources/          # Icons, templates, documentation
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Security

- **API Keys**: Stored encrypted using industry-standard cryptography
- **Communication**: All AI provider communication uses HTTPS/WSS
- **Local Storage**: Configuration and logs stored in user directory only
- **No Telemetry**: No usage data sent without explicit user consent

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Wiki](https://github.com/username/freecad-ai-addon/wiki)
- **Issues**: [GitHub Issues](https://github.com/username/freecad-ai-addon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/freecad-ai-addon/discussions)
- **FreeCAD Forum**: [AI Addon Thread](https://forum.freecad.org)

## Acknowledgments

- FreeCAD community for the excellent CAD platform
- Model Context Protocol team for the integration standard
- AI provider teams for their APIs and tools

---

**Made with ❤️ for the FreeCAD community**
