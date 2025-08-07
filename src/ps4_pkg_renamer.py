import os
import argparse
import subprocess
import json
import re

def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def read_pkg_info(pkg_path):
    try:
        result = subprocess.run(['ps4-pkg-info.exe', '--json', pkg_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"ps4-pkg-info error: {result.stderr.strip()}")
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Failed to read info from {pkg_path}: {e}")
        return None

def format_new_name(info, fmt):
    if not info:
        return None
    title_id = info.get('title_id', 'UNKNOWN')
    title_name = info.get('title', 'Unknown Title')
    version = info.get('app_version', '1.00')
    pkg_type = info.get('category', 'Unknown')
    return sanitize_filename(fmt.format(
        title_id=title_id,
        title_name=title_name,
        version=version,
        pkg_type=pkg_type
    )) + '.pkg'

def rename_pkg(pkg_path, fmt):
    info = read_pkg_info(pkg_path)
    if not info:
        print(f"Skipping {pkg_path}")
        return
    new_name = format_new_name(info, fmt)
    if not new_name:
        print(f"Skipping {pkg_path}")
        return
    new_path = os.path.join(os.path.dirname(pkg_path), new_name)
    if os.path.exists(new_path):
        print(f"Target file exists: {new_path}, skipping rename.")
        return
    os.rename(pkg_path, new_path)
    print(f"Renamed:\n  {os.path.basename(pkg_path)}\n→ {new_name}")

def main():
    parser = argparse.ArgumentParser(description='PS4 PKG Renamer')
    parser.add_argument('path', help='File or directory path')
    parser.add_argument('--format', default='{title_id} - {title_name} - v{version} - {pkg_type}', help='Rename format')
    args = parser.parse_args()

    if os.path.isdir(args.path):
        for f in os.listdir(args.path):
            full_path = os.path.join(args.path, f)
            if os.path.isfile(full_path) and f.lower().endswith('.pkg'):
                rename_pkg(full_path, args.format)
    elif os.path.isfile(args.path) and args.path.lower().endswith('.pkg'):
        rename_pkg(args.path, args.format)
    else:
        print("Please specify a .pkg file or a directory containing .pkg files.")

if __name__ == '__main__':
    main()
