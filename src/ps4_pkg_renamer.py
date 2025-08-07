import os
import re
import subprocess
import argparse

def parse_orbis_pub_chk_output(output):
    info = {}
    # 简单正则示例，需根据 orbis-pub-chk 实际输出调整
    title_id_match = re.search(r'Title ID\s+:\s+([^\r\n]+)', output)
    title_name_match = re.search(r'Title Name\s+:\s+([^\r\n]+)', output)
    version_match = re.search(r'App Version\s+:\s+([^\r\n]+)', output)
    pkg_type_match = re.search(r'Package Type\s+:\s+([^\r\n]+)', output)

    if title_id_match:
        info['title_id'] = title_id_match.group(1).strip()
    if title_name_match:
        info['title_name'] = title_name_match.group(1).strip()
    if version_match:
        info['version'] = version_match.group(1).strip()
    if pkg_type_match:
        info['pkg_type'] = pkg_type_match.group(1).strip()

    return info

def get_pkg_info(pkg_path, orbis_pub_chk_path='orbis-pub-chk.exe'):
    try:
        result = subprocess.run([orbis_pub_chk_path, pkg_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running orbis-pub-chk on {pkg_path}")
            return None
        return parse_orbis_pub_chk_output(result.stdout)
    except Exception as e:
        print(f"Exception running orbis-pub-chk: {e}")
        return None

def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def format_new_name(info, fmt):
    if not info:
        return None
    return sanitize_filename(fmt.format(
        title_id=info.get('title_id', 'UNKNOWN'),
        title_name=info.get('title_name', 'Unknown Title'),
        version=info.get('version', '1.00'),
        pkg_type=info.get('pkg_type', 'Unknown')
    )) + '.pkg'

def rename_pkg(pkg_path, fmt, orbis_pub_chk_path):
    info = get_pkg_info(pkg_path, orbis_pub_chk_path)
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
    parser = argparse.ArgumentParser(description='PS4 PKG Renamer (orbis-pub-chk)')
    parser.add_argument('path', help='File or directory path')
    parser.add_argument('--format', default='{title_id} - {title_name} - v{version} - {pkg_type}', help='Rename format')
    parser.add_argument('--orbis-path', default='orbis-pub-chk.exe', help='Path to orbis-pub-chk executable')
    args = parser.parse_args()

    if os.path.isdir(args.path):
        for f in os.listdir(args.path):
            full_path = os.path.join(args.path, f)
            if os.path.isfile(full_path) and f.lower().endswith('.pkg'):
                rename_pkg(full_path, args.format, args.orbis_path)
    elif os.path.isfile(args.path) and args.path.lower().endswith('.pkg'):
        rename_pkg(args.path, args.format, args.orbis_path)
    else:
        print("Please specify a .pkg file or a directory containing .pkg files.")

if __name__ == '__main__':
    main()
