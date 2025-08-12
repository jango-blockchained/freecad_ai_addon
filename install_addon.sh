#!/bin/bash
# FreeCAD AI Addon Installation Script
# This script symlinks the addon into FreeCAD's Mod directory for development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    # Log to stderr so command substitutions don't capture status lines
    echo -e "${BLUE}[INFO]${NC} $1" 1>&2
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" 1>&2
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" 1>&2
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" 1>&2
}

# Default FreeCAD Mod directories (in order of preference)
FREECAD_MOD_DIRS=(
    "$HOME/.local/share/FreeCAD/Mod"
    "$HOME/.FreeCAD/Mod"
    "/usr/share/freecad/Mod"
    "/usr/local/share/freecad/Mod"
)

# Get the current directory (should be the addon root)
ADDON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADDON_NAME="freecad_ai_addon"

print_status "FreeCAD AI Addon Installation Script"
echo "======================================"
echo

# Function to find FreeCAD Mod directory
find_freecad_mod_dir() {
    for dir in "${FREECAD_MOD_DIRS[@]}"; do
        if [ -d "$(dirname "$dir")" ]; then
            # Parent directory exists, we can create the Mod dir if needed
            if [ ! -d "$dir" ]; then
                print_status "Creating FreeCAD Mod directory: $dir"
                mkdir -p "$dir"
            fi
            echo "$dir"
            return 0
        fi
    done
    return 1
}

# Function to check if FreeCAD is installed
check_freecad() {
    if command -v freecad >/dev/null 2>&1 || command -v FreeCAD >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main installation function
install_addon() {
    print_status "Checking FreeCAD installation..."
    
    if ! check_freecad; then
        print_warning "FreeCAD not found in PATH. Installing anyway..."
    else
        print_success "FreeCAD found"
    fi
    
    print_status "Looking for FreeCAD Mod directory..."
    
    MOD_DIR=$(find_freecad_mod_dir)
    if [ $? -ne 0 ] || [ -z "$MOD_DIR" ]; then
        print_error "Could not find or create FreeCAD Mod directory"
        echo
        echo "Please create one of these directories manually:"
        for dir in "${FREECAD_MOD_DIRS[@]}"; do
            echo "  - $dir"
        done
        echo
        echo "Then run this script again."
        exit 1
    fi
    
    print_success "Found FreeCAD Mod directory: $MOD_DIR"
    
    # Target symlink path
    TARGET_LINK="$MOD_DIR/$ADDON_NAME"
    
    # Check if link already exists
    if [ -L "$TARGET_LINK" ]; then
        print_warning "Symlink already exists: $TARGET_LINK"
        
        # Check if it points to the current directory
        CURRENT_TARGET=$(readlink "$TARGET_LINK")
        if [ "$CURRENT_TARGET" = "$ADDON_DIR" ]; then
            print_success "Symlink already points to current directory"
            return 0
        else
            print_status "Removing old symlink (pointed to: $CURRENT_TARGET)"
            rm "$TARGET_LINK"
        fi
    elif [ -e "$TARGET_LINK" ]; then
        # Handle existing non-symlink (e.g., directory from copy-based install)
        BACKUP="$TARGET_LINK.backup.$(date +%Y%m%d%H%M%S)"
        print_warning "Target exists and is not a symlink: $TARGET_LINK"
        print_status "Moving existing target to backup: $BACKUP"
        mv "$TARGET_LINK" "$BACKUP"
    fi
    
    # Create the symlink
    print_status "Creating symlink..."
    ln -s "$ADDON_DIR" "$TARGET_LINK"
    
    if [ $? -eq 0 ]; then
        print_success "Symlink created successfully!"
        echo
        echo "Installation Details:"
        echo "  Source: $ADDON_DIR"
        echo "  Target: $TARGET_LINK"
        echo
        echo "The addon should now appear in FreeCAD's Addon Manager or Workbench list."
    else
        print_error "Failed to create symlink"
        exit 1
    fi
}

# Function to uninstall the addon
uninstall_addon() {
    print_status "Uninstalling FreeCAD AI Addon..."
    
    for mod_dir in "${FREECAD_MOD_DIRS[@]}"; do
        target_link="$mod_dir/$ADDON_NAME"
        
        if [ -L "$target_link" ]; then
            print_status "Removing symlink: $target_link"
            rm "$target_link"
            print_success "Symlink removed"
            return 0
        elif [ -e "$target_link" ]; then
            # For convenience, move existing directory to a backup instead of deleting
            BACKUP="$target_link.backup.$(date +%Y%m%d%H%M%S)"
            print_warning "Found non-symlink at: $target_link"
            print_status "Moving existing target to backup: $BACKUP"
            mv "$target_link" "$BACKUP"
            print_success "Moved to backup: $BACKUP"
            return 0
        fi
    done
    
    print_warning "No symlinks found to remove"
}

# Function to check installation status
check_installation() {
    print_status "Checking installation status..."
    
    found=false
    for mod_dir in "${FREECAD_MOD_DIRS[@]}"; do
        target_link="$mod_dir/$ADDON_NAME"
        
        if [ -L "$target_link" ]; then
            link_target=$(readlink "$target_link")
            print_success "Found symlink: $target_link -> $link_target"
            
            if [ "$link_target" = "$ADDON_DIR" ]; then
                print_success "Symlink points to current directory ✓"
            else
                print_warning "Symlink points to different directory"
            fi
            found=true
        elif [ -e "$target_link" ]; then
            print_warning "Found non-symlink at: $target_link"
            found=true
        fi
    done
    
    if [ "$found" = false ]; then
        print_status "No installation found"
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [install|uninstall|check|help]"
    echo
    echo "Commands:"
    echo "  install    - Install the addon by creating a symlink (default)"
    echo "  uninstall  - Remove the addon symlink"
    echo "  check      - Check current installation status"
    echo "  help       - Show this help message"
    echo
    echo "The addon will be installed to one of these locations:"
    for dir in "${FREECAD_MOD_DIRS[@]}"; do
        echo "  - $dir/$ADDON_NAME"
    done
    echo
}

# Main script logic
case "${1:-install}" in
    "install")
        install_addon
        ;;
    "uninstall")
        uninstall_addon
        ;;
    "check")
        check_installation
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_usage
        exit 1
        ;;
esac

echo
print_status "Done!"
