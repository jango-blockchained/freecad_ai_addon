#!/bin/bash

# Fix locale warnings in git commits
# This script helps resolve the "cannot change locale" warning

echo "🔧 Fixing locale configuration for git commits..."

# Check current locale settings
echo "Current locale settings:"
locale

# Set fallback locales that are commonly available
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Alternative: Use POSIX locale if UTF-8 is not available
if ! locale -a | grep -q "C.UTF-8"; then
    echo "C.UTF-8 not available, falling back to POSIX"
    export LC_ALL=POSIX
    export LANG=POSIX
fi

# Add to shell profile for persistence
SHELL_RC=""
if [ -f ~/.bashrc ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f ~/.zshrc ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [ -n "$SHELL_RC" ]; then
    echo "Adding locale settings to $SHELL_RC"
    if ! grep -q "LC_ALL=C.UTF-8" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Fix locale warnings in git/pre-commit" >> "$SHELL_RC"
        echo "export LC_ALL=C.UTF-8" >> "$SHELL_RC"
        echo "export LANG=C.UTF-8" >> "$SHELL_RC"
    fi
fi

echo "✅ Locale configuration updated"
echo "   You may need to restart your terminal or run: source $SHELL_RC"
