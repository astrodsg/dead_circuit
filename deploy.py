#!env python
""" Run by parent deploy script


https://learn.adafruit.com/circuitpython-hardware-lis3dh-accelerometer/software

"""
import zipfile
import os
import sys
import subprocess
import urllib.request


# copy from the project
PROJECTS_DIR = './projects'

# copy files to the usb volume
CIRCUITPY_DIR = '/Volumes/CIRCUITPY'

# copy package requirements
REQUIREMENTS_FILENAME = 'requirements.txt'

# download circuit libraries for requirements
DOWNLOAD_DIR = './untracked_downloads'
DOWNLOAD_SOURCES = {
    'circuitpython_busdriver': (
        "https://github.com/adafruit/Adafruit_CircuitPython_BusDevice/"
        "releases/download/"
        "2.2.11/adafruit-circuitpython-bus-device-py-2.2.11.zip"
    ),
    'circuitpython_lis3dh': (
        "https://github.com/adafruit/Adafruit_CircuitPython_LIS3DH/"
        "releases/download/"
        "4.3.5/adafruit-circuitpython-lis3dh-py-4.3.5.zip"
    ),
    'circuitpython_bundle': (
        "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/"
        "releases/download/"
        "20190601/adafruit-circuitpython-bundle-py-20190601.zip"
    )
}


def yes_no_from_user(msg):
    msg = msg + ' [y/n]: '
    while True:
        user_input = input(msg)
        if user_input == 'n':
            return False
        elif user_input == 'y':
            return True
        print('enter [y]es or [n]o')


def get_project_from_user():
    if len(sys.argv) == 2:
        project_name = sys.argv[1]
    else:
        project_name = input('provide project name: ')

    project_dir = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.isdir(project_dir):
        projects = os.listdir(PROJECTS_DIR)
        raise FileNotFoundError(
            f'no project named {project_name} at {project_dir}\n'
            f'please choose from {projects}'
        )
    return project_dir


def delete_files_after_checking_with_user(destination):
    print(f"""
    WARNING: About to remove files from {CIRCUITPY_DIR} type 'n' to abort.
    """)
    for name in os.listdir(destination):
        if name.startswith('.'):
            continue
        file_or_dir = os.path.join(destination, name)
        if yes_no_from_user(f'remove {file_or_dir}?'):
            subprocess.check_call(['rm', '-rf', file_or_dir])
        else:
            print('stopping')
            sys.exit(1)


def copy_files_to_circuitpy(source, destination=None):
    if destination is None:
        destination = os.path.abspath(CIRCUITPY_DIR)
    cmd = f"cp -rp {source} {destination}"
    print(cmd)
    status, msg = subprocess.getstatusoutput(cmd)
    if status != 0:
        raise IOError(msg)


def get_project_requirements(project_dir):
    requirements = []
    requirements_file = os.path.join(project_dir, REQUIREMENTS_FILENAME)
    if not os.path.exists(requirements_file):
        print(f'no requirements needed: {requirements_file}')
    else:
        with open(requirements_file) as fp:
            for line in fp:
                pypackage = line.rstrip().strip()
                if pypackage == '':
                    continue
                requirements.append(pypackage)
    return requirements


def download(url):
    output_file = os.path.join(DOWNLOAD_DIR, os.path.basename(url))
    urllib.request.urlretrieve(url, output_file)
    with zipfile.ZipFile(output_file) as zp:
        zp.extractall(os.path.dirname(output_file))


def download_sources():
    if not os.path.isdir(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    for name, url in DOWNLOAD_SOURCES.items():
        print(f'downloading {name} from {url}')
        download(url)


def find_requirement(requirement):
    for dirname in os.listdir(DOWNLOAD_DIR):
        dirpath = os.path.join(DOWNLOAD_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue

        print(dirpath)
        # e.g. untracked_downlaods/adafruit-circuitpython-bundle-py-20190601/lib
        lib_dir = os.path.join(dirpath, 'lib')
        if not os.path.isdir(lib_dir):
            raise FileNotFoundError(f'no lib directory for {dirpath}')

        # e.g. untracked_downlaods/adafruit-circuitpython-bundle-py-20190601/lib/[requirement]*  # noqa
        package_dir = os.path.join(lib_dir, requirement)
        if os.path.isdir(package_dir):
            return package_dir

        package_module = os.path.join(lib_dir, requirement, '.py')
        if os.path.exists(package_module):
            return package_module

    raise FileNotFoundError(f'could not find requirement {requirement}')


if __name__ == "__main__":
    if not os.path.isdir(CIRCUITPY_DIR):
        raise FileNotFoundError(f'Please mount circuitpy {CIRCUITPY_DIR}')

    # 1. get project directory
    project_dir = get_project_from_user()

    # 1. delete files
    delete_files_after_checking_with_user(CIRCUITPY_DIR)

    # 1. copy all files from the project to the circuitpy
    copy_files_to_circuitpy(os.path.join(project_dir, '*'))

    # 1. get circuitpy requirements
    requirements = get_project_requirements(project_dir)
    if len(requirements) == 0:
        sys.exit(0)

    # 1. download all possible requirements locally
    if not os.path.isdir(DOWNLOAD_DIR):
        download_sources()

    # 1. find and copy
    lib_destination = os.path.join(CIRCUITPY_DIR, 'lib')
    if not os.path.isdir(lib_destination):
        os.mkdir(lib_destination)
    for pypackage in requirements:
        pypackage_location = find_requirement(pypackage)
        copy_files_to_circuitpy(pypackage_location, lib_destination + '/')
