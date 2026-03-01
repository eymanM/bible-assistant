import os
import subprocess
import sys

def get_staged_files():
    """Returns a list of files that are staged for commit."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        return [line.strip() for line in result.stdout.split('\n') if line.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error getting staged files: {e}", file=sys.stderr)
        return []

def main():
    version_file = 'VERSION'
    if not os.path.exists(version_file):
        print(f"File {version_file} does not exist.", file=sys.stderr)
        return 1

    staged_files = get_staged_files()
    
    # If the user has manually staged the VERSION file, skip auto-bumping.
    if version_file in staged_files:
        print("Manual version bump detected. Skipping automatic patch bump.", file=sys.stderr)
        return 0

    try:
        with open(version_file, 'r') as f:
            version = f.read().strip()
    except Exception as e:
        print(f"Error reading version file: {e}", file=sys.stderr)
        return 1

    parts = version.split('.')
    if len(parts) != 3:
        print(f"Invalid version format: {version}. Expected X.Y.Z", file=sys.stderr)
        return 1
        
    try:
        patch = int(parts[2])
    except ValueError:
        print(f"Invalid patch version: {parts[2]}.", file=sys.stderr)
        return 1

    # Bump patch version
    patch += 1
    new_version = f"{parts[0]}.{parts[1]}.{patch}"

    try:
        with open(version_file, 'w') as f:
            f.write(new_version)
    except Exception as e:
        print(f"Error writing to version file: {e}", file=sys.stderr)
        return 1

    try:
        subprocess.run(['git', 'add', version_file], check=True)
        print(f"Automatically bumped version from {version} to {new_version}.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error staging version file: {e}", file=sys.stderr)
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
