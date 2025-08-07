#!/usr/bin/env python3
"""
FreeCAD AI Addon Installation Script (Python)

This script can be run from within FreeCAD or as a standalone Python script
to install the addon by creating symlinks to the FreeCAD Mod directory.

Usage:
    python install_addon.py [install|uninstall|check]

Or from within FreeCAD:
    exec(open("install_addon.py").read())
"""

import os
import sys
import platform
from pathlib import Path


def get_freecad_mod_directories():
    """Get possible FreeCAD Mod directories based on the operating system."""
    system = platform.system()
    home = Path.home()

    if system == "Linux":
        return [
            home / ".local/share/FreeCAD/Mod",
            home / ".FreeCAD/Mod",
            Path("/usr/share/freecad/Mod"),
            Path("/usr/local/share/freecad/Mod"),
        ]
    elif system == "Windows":
        appdata = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
        return [
            appdata / "FreeCAD/Mod",
            home / ".FreeCAD/Mod",
            Path("C:/Program Files/FreeCAD/Mod"),
        ]
    elif system == "Darwin":  # macOS
        return [
            home / "Library/Application Support/FreeCAD/Mod",
            home / ".FreeCAD/Mod",
            Path("/Applications/FreeCAD.app/Contents/Mod"),
        ]
    else:
        return [home / ".FreeCAD/Mod"]


def find_freecad_mod_directory():
    """Find the first available FreeCAD Mod directory."""
    for mod_dir in get_freecad_mod_directories():
        if mod_dir.parent.exists():
            # Parent directory exists, we can create Mod if needed
            mod_dir.mkdir(parents=True, exist_ok=True)
            return mod_dir
    return None


def get_addon_directory():
    """Get the current addon directory."""
    return Path(__file__).parent.absolute()


def create_symlink(source, target):
    """Create a symlink, handling Windows junction points."""
    try:
        if platform.system() == "Windows":
            # Use junction points on Windows
            import subprocess

            result = subprocess.run(
                ["mklink", "/J", str(target), str(source)],
                shell=True,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        else:
            # Use symlinks on Unix-like systems
            target.symlink_to(source)
            return True
    except Exception as e:
        print(f"Error creating symlink: {e}")
        return False


def remove_symlink(target):
    """Remove a symlink or junction point."""
    try:
        if target.is_symlink() or (platform.system() == "Windows" and target.is_dir()):
            if platform.system() == "Windows":
                # Remove junction point
                import subprocess

                result = subprocess.run(
                    ["rmdir", str(target)], shell=True, capture_output=True
                )
                return result.returncode == 0
            else:
                target.unlink()
                return True
    except Exception as e:
        print(f"Error removing symlink: {e}")
        return False
    return False


def install_addon():
    """Install the addon by creating a symlink."""
    print("FreeCAD AI Addon Installation (Python)")
    print("=====================================")
    print()

    addon_dir = get_addon_directory()
    addon_name = "freecad-ai-addon"

    print(f"Addon directory: {addon_dir}")

    # Find FreeCAD Mod directory
    mod_dir = find_freecad_mod_directory()
    if not mod_dir:
        print("ERROR: Could not find or create FreeCAD Mod directory")
        print("Possible locations:")
        for dir_path in get_freecad_mod_directories():
            print(f"  - {dir_path}")
        return False

    print(f"FreeCAD Mod directory: {mod_dir}")

    target_link = mod_dir / addon_name

    # Check if target already exists
    if target_link.exists():
        if target_link.is_symlink() or (
            platform.system() == "Windows" and target_link.is_dir()
        ):
            print(f"Removing existing symlink: {target_link}")
            if not remove_symlink(target_link):
                print("ERROR: Failed to remove existing symlink")
                return False
        else:
            print(f"ERROR: Target exists but is not a symlink: {target_link}")
            print("Please remove it manually and run this script again")
            return False

    # Create the symlink
    print("Creating symlink...")
    if create_symlink(addon_dir, target_link):
        print("SUCCESS: Symlink created successfully!")
        print()
        print("Installation Details:")
        print(f"  Source: {addon_dir}")
        print(f"  Target: {target_link}")
        print()
        print(
            "The addon should now appear in FreeCAD's Addon Manager or Workbench list."
        )
        return True
    else:
        print("ERROR: Failed to create symlink")
        if platform.system() == "Windows":
            print("Make sure you're running as Administrator")
        return False


def uninstall_addon():
    """Uninstall the addon by removing symlinks."""
    print("Uninstalling FreeCAD AI Addon...")

    addon_name = "freecad-ai-addon"
    found = False

    for mod_dir in get_freecad_mod_directories():
        target_link = mod_dir / addon_name

        if target_link.exists():
            if target_link.is_symlink() or (
                platform.system() == "Windows" and target_link.is_dir()
            ):
                print(f"Removing symlink: {target_link}")
                if remove_symlink(target_link):
                    print("SUCCESS: Symlink removed")
                    found = True
                else:
                    print("ERROR: Failed to remove symlink")
            else:
                print(f"WARNING: Found non-symlink at: {target_link}")
                print("Please remove it manually")
                found = True

    if not found:
        print("No symlinks found to remove")

    return found


def check_installation():
    """Check the current installation status."""
    print("Checking installation status...")

    addon_dir = get_addon_directory()
    addon_name = "freecad-ai-addon"
    found = False

    for mod_dir in get_freecad_mod_directories():
        target_link = mod_dir / addon_name

        if target_link.exists():
            if target_link.is_symlink():
                link_target = target_link.readlink()
                print(f"Found symlink: {target_link} -> {link_target}")
                if link_target.resolve() == addon_dir:
                    print("✓ Symlink points to current directory")
                else:
                    print("⚠ Symlink points to different directory")
                found = True
            elif platform.system() == "Windows" and target_link.is_dir():
                print(f"Found junction: {target_link}")
                found = True
            else:
                print(f"Found non-symlink at: {target_link}")
                found = True

    if not found:
        print("No installation found")

    return found


def show_usage():
    """Show usage information."""
    print("Usage: python install_addon.py [install|uninstall|check|help]")
    print()
    print("Commands:")
    print("  install    - Install the addon by creating a symlink (default)")
    print("  uninstall  - Remove the addon symlink")
    print("  check      - Check current installation status")
    print("  help       - Show this help message")
    print()
    print("The addon will be installed to one of these locations:")
    for mod_dir in get_freecad_mod_directories():
        print(f"  - {mod_dir}/freecad-ai-addon")
    print()


def main():
    """Main function."""
    # Check if running from within FreeCAD
    try:
        import FreeCAD

        print("Running from within FreeCAD")
        in_freecad = True
    except ImportError:
        in_freecad = False

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "install"

    if command == "install":
        success = install_addon()
    elif command == "uninstall":
        success = uninstall_addon()
    elif command == "check":
        success = check_installation()
    elif command in ["help", "-h", "--help"]:
        show_usage()
        return
    else:
        print(f"Unknown command: {command}")
        show_usage()
        return

    print()
    if success:
        print("Done!")
    else:
        print("Operation completed with warnings or errors.")

    # If running from within FreeCAD, don't exit
    if not in_freecad:
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
