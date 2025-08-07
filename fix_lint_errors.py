#!/usr/bin/env python3
"""
Script to fix non-cosmetic lint errors in the FreeCAD AI Addon project.
This script focuses on functional issues and ignores purely cosmetic formatting.
"""

import os
import re
import subprocess
from pathlib import Path

# Error types to fix (non-cosmetic)
CRITICAL_ERRORS = [
    "F401",  # unused imports
    "F541",  # f-string is missing placeholders
    "F841",  # local variable assigned but never used
    "E402",  # module level import not at top of file
    "E306",  # expected 1 blank line before a nested definition
    "E712",  # comparison to False should be 'if cond is False:' or 'if not cond:'
    "E722",  # do not use bare 'except'
    "E128",  # continuation line under-indented for visual indent
]


def run_command(cmd):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        return "", str(e), 1


def get_lint_errors():
    """Get flake8 errors for critical error types only."""
    error_select = ",".join(CRITICAL_ERRORS)
    cmd = f"flake8 . --exclude=__pycache__,*.pyc --select={error_select} --format='%(path)s:%(row)d:%(col)d: %(code)s %(text)s'"
    stdout, stderr, returncode = run_command(cmd)

    errors = []
    for line in stdout.strip().split("\n"):
        if line:
            parts = line.split(": ", 2)
            if len(parts) >= 3:
                location = parts[0]
                error_code = parts[1]
                message = parts[2]
                file_path, line_col = location.rsplit(":", 1)
                line_num, col_num = line_col.split(":")
                errors.append(
                    {
                        "file": file_path,
                        "line": int(line_num),
                        "col": int(col_num),
                        "code": error_code,
                        "message": message,
                    }
                )

    return errors


def fix_unused_imports(file_path, errors):
    """Remove unused imports."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Group F401 errors by line number
    unused_imports = {}
    for error in errors:
        if error["code"] == "F401":
            unused_imports[error["line"]] = error["message"]

    # Remove unused import lines
    new_lines = []
    for i, line in enumerate(lines, 1):
        if i in unused_imports:
            # Check if it's a multi-import line
            if "," in line and "import" in line:
                # Extract the unused import name from the error message
                message = unused_imports[i]
                if "imported but unused" in message:
                    unused_name = message.split("'")[1] if "'" in message else ""
                    if unused_name:
                        # Remove the specific import from the line
                        line = remove_specific_import(line, unused_name)
                        if (
                            line.strip()
                        ):  # Only keep the line if there are still imports
                            new_lines.append(line)
                    else:
                        # Skip the entire line
                        pass
                else:
                    new_lines.append(line)
            else:
                # Skip the entire import line
                pass
        else:
            new_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)


def remove_specific_import(line, unused_name):
    """Remove a specific import from a line containing multiple imports."""
    # Handle different import patterns
    if "from" in line and "import" in line:
        # from module import a, b, c
        parts = line.split("import", 1)
        if len(parts) == 2:
            imports = parts[1].strip()
            import_list = [imp.strip() for imp in imports.split(",")]
            new_imports = [imp for imp in import_list if imp != unused_name]
            if new_imports:
                line = parts[0] + "import " + ", ".join(new_imports) + "\n"
            else:
                line = ""
    elif "import" in line:
        # import a, b, c
        parts = line.split("import", 1)
        if len(parts) == 2:
            imports = parts[1].strip()
            import_list = [imp.strip() for imp in imports.split(",")]
            new_imports = [imp for imp in import_list if imp != unused_name]
            if new_imports:
                line = parts[0] + "import " + ", ".join(new_imports) + "\n"
            else:
                line = ""

    return line


def fix_f_string_placeholders(file_path, errors):
    """Fix f-strings missing placeholders by converting to regular strings."""
    with open(file_path, "r") as f:
        content = f.read()

    lines = content.split("\n")

    for error in errors:
        if error["code"] == "F541":
            line_num = error["line"] - 1
            if line_num < len(lines):
                line = lines[line_num]
                # Find f-strings and convert to regular strings if no placeholders
                line = re.sub(
                    r'f"([^"]*)"',
                    lambda m: (
                        f'"{m.group(1)}"' if "{" not in m.group(1) else m.group(0)
                    ),
                    line,
                )
                line = re.sub(
                    r"f'([^']*)'",
                    lambda m: (
                        f"'{m.group(1)}'" if "{" not in m.group(1) else m.group(0)
                    ),
                    line,
                )
                lines[line_num] = line

    with open(file_path, "w") as f:
        f.write("\n".join(lines))


def fix_comparison_to_false(file_path, errors):
    """Fix comparison to False."""
    with open(file_path, "r") as f:
        content = f.read()

    lines = content.split("\n")

    for error in errors:
        if error["code"] == "E712":
            line_num = error["line"] - 1
            if line_num < len(lines):
                line = lines[line_num]
                # Replace == False with 'is False' and != False with 'is not False'
                line = re.sub(r"(\w+)\s*==\s*False", r"\1 is False", line)
                line = re.sub(r"(\w+)\s*!=\s*False", r"\1 is not False", line)
                lines[line_num] = line

    with open(file_path, "w") as f:
        f.write("\n".join(lines))


def fix_bare_except(file_path, errors):
    """Fix bare except clauses."""
    with open(file_path, "r") as f:
        content = f.read()

    lines = content.split("\n")

    for error in errors:
        if error["code"] == "E722":
            line_num = error["line"] - 1
            if line_num < len(lines):
                line = lines[line_num]
                # Replace bare except with except Exception
                line = re.sub(r"except\s*:", "except Exception:", line)
                lines[line_num] = line

    with open(file_path, "w") as f:
        f.write("\n".join(lines))


def main():
    """Main function to fix lint errors."""
    print("Getting lint errors...")
    errors = get_lint_errors()

    if not errors:
        print("No critical lint errors found!")
        return

    print(f"Found {len(errors)} critical lint errors to fix.")

    # Group errors by file
    files_to_fix = {}
    for error in errors:
        file_path = error["file"]
        if file_path not in files_to_fix:
            files_to_fix[file_path] = []
        files_to_fix[file_path].append(error)

    # Fix each file
    for file_path, file_errors in files_to_fix.items():
        print(f"Fixing {file_path}...")

        # Categorize errors for this file
        f401_errors = [e for e in file_errors if e["code"] == "F401"]
        f541_errors = [e for e in file_errors if e["code"] == "F541"]
        e712_errors = [e for e in file_errors if e["code"] == "E712"]
        e722_errors = [e for e in file_errors if e["code"] == "E722"]

        # Apply fixes
        if f401_errors:
            fix_unused_imports(file_path, f401_errors)

        if f541_errors:
            fix_f_string_placeholders(file_path, f541_errors)

        if e712_errors:
            fix_comparison_to_false(file_path, e712_errors)

        if e722_errors:
            fix_bare_except(file_path, e722_errors)

    print("Finished fixing critical lint errors!")
    print("Run 'flake8' again to see remaining issues.")


if __name__ == "__main__":
    main()
