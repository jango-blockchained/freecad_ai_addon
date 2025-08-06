# FreeCAD AI Addon Installation Guide

This document provides detailed instructions for installing the FreeCAD AI Addon using various methods, including the provided installation scripts.

## 🚀 Quick Installation (Recommended for Developers)

The easiest way to install the addon for development or testing is using the provided installation scripts that create symlinks to your FreeCAD Mod directory.

### Linux/macOS

```bash
git clone https://github.com/username/freecad-ai-addon.git
cd freecad-ai-addon
./install_addon.sh install
```

### Windows

```cmd
git clone https://github.com/username/freecad-ai-addon.git
cd freecad-ai-addon
install_addon.bat install
```

### Cross-Platform Python Script

```bash
python install_addon.py install
```

## 📋 Available Installation Scripts

The addon includes three installation scripts for different preferences:

| Script | Platform | Description |
|--------|----------|-------------|
| `install_addon.sh` | Linux/macOS | Bash script with detailed output |
| `install_addon.bat` | Windows | Batch file for Windows systems |
| `install_addon.py` | Cross-platform | Python script that works everywhere |

## 🔧 Installation Script Commands

All scripts support the following commands:

### Install
Creates a symlink from the addon directory to FreeCAD's Mod folder:

```bash
./install_addon.sh install      # Linux/macOS
install_addon.bat install       # Windows  
python install_addon.py install # Cross-platform
```

### Check Status
Verifies if the addon is currently installed:

```bash
./install_addon.sh check        # Linux/macOS
install_addon.bat check         # Windows
python install_addon.py check   # Cross-platform
```

### Uninstall
Removes the symlink (keeps your development files intact):

```bash
./install_addon.sh uninstall    # Linux/macOS
install_addon.bat uninstall     # Windows
python install_addon.py uninstall # Cross-platform
```

### Help
Shows usage information:

```bash
./install_addon.sh help         # Linux/macOS
install_addon.bat help          # Windows
python install_addon.py help    # Cross-platform
```

## 📁 FreeCAD Mod Directory Locations

The scripts automatically detect and use the appropriate FreeCAD Mod directory:

### Linux
- `~/.local/share/FreeCAD/Mod/` (preferred)
- `~/.FreeCAD/Mod/`
- `/usr/share/freecad/Mod/`
- `/usr/local/share/freecad/Mod/`

### Windows
- `%APPDATA%\FreeCAD\Mod\` (preferred)
- `%USERPROFILE%\.FreeCAD\Mod\`
- `C:\Program Files\FreeCAD\Mod\`

### macOS
- `~/Library/Application Support/FreeCAD/Mod/` (preferred)
- `~/.FreeCAD/Mod/`
- `/Applications/FreeCAD.app/Contents/Mod/`

## ✅ Advantages of Symlink Installation

Using the installation scripts provides several benefits:

1. **Live Development**: Changes to the code are immediately available in FreeCAD
2. **Easy Updates**: Simply run `git pull` to get the latest changes
3. **Clean Uninstall**: Remove the addon without affecting your development files
4. **Version Control**: Keep your addon under git version control
5. **Multiple Versions**: Easy to switch between different branches or versions

## 🛠️ Installation Process Details

### What the Scripts Do

1. **Detect FreeCAD Installation**: Locate the appropriate FreeCAD Mod directory
2. **Create Directory**: Ensure the Mod directory exists
3. **Remove Existing**: Clean up any previous installations
4. **Create Symlink**: Link the addon directory to `freecad-ai-addon/` in Mod
5. **Verify Installation**: Confirm the symlink was created successfully

### Symlink vs Junction (Windows)

On Windows, the scripts use **directory junctions** instead of symlinks:
- Junctions work without administrator privileges
- Compatible with all Windows versions
- Function identically to symlinks for this use case

## 🔍 Troubleshooting

### Permission Issues (Linux/macOS)
If you get permission errors:
```bash
chmod +x install_addon.sh
sudo ./install_addon.sh install
```

### Administrator Rights (Windows)
If the Windows script fails:
1. Right-click Command Prompt
2. Select "Run as Administrator"
3. Navigate to the addon directory
4. Run `install_addon.bat install`

### FreeCAD Not Found
If FreeCAD directories don't exist:
1. Install FreeCAD first
2. Run FreeCAD once to create user directories
3. Run the installation script again

### Existing Installation
If you have a previous installation:
```bash
./install_addon.sh uninstall  # Remove old version
./install_addon.sh install    # Install new version
```

## 🔄 Alternative Installation Methods

### Manual Copy Installation
1. Copy the entire addon folder to your FreeCAD Mod directory
2. Rename it to `freecad-ai-addon`
3. Restart FreeCAD

### ZIP Installation
1. Download the addon as a ZIP file
2. Extract to your FreeCAD Mod directory
3. Ensure the folder is named `freecad-ai-addon`
4. Restart FreeCAD

### FreeCAD Addon Manager
Once the addon is published:
1. Open FreeCAD → Tools → Addon Manager
2. Search for "FreeCAD AI Addon"
3. Click Install

## ✅ Verifying Installation

After installation, verify the addon is working:

1. **Restart FreeCAD**
2. **Check Workbench List**: Look for "AI Assistant" in the workbench dropdown
3. **Check Addon Manager**: The addon should appear in Tools → Addon Manager
4. **Test Loading**: Switch to the AI Assistant workbench

### Expected Files in FreeCAD Mod Directory

After successful installation, you should see:
```
~/.local/share/FreeCAD/Mod/freecad-ai-addon/  (symlink)
├── freecad_ai_addon/
├── InitGui.py
├── Init.py
├── package.xml
└── ...
```

## 🔧 Development Workflow

With symlink installation, your development workflow becomes:

1. **Make Changes**: Edit files in your development directory
2. **Test in FreeCAD**: Changes are immediately available
3. **Restart if Needed**: Some changes require FreeCAD restart
4. **Commit Changes**: Use git to version control your work
5. **Update Installation**: Run `git pull` to get latest changes

## 🆘 Getting Help

If you encounter issues with installation:

1. **Check Status**: Run the check command to see current state
2. **Review Logs**: Installation scripts show detailed output
3. **Try Alternative**: Use a different installation script
4. **Manual Installation**: Fall back to manual copy method
5. **Report Issues**: Open an issue on the project repository

---

**Note**: These installation scripts are designed for development and testing. For production use, consider using the FreeCAD Addon Manager when available.
