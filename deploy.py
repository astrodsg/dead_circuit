#!env python
""" Run by parent deploy script


https://learn.adafruit.com/circuitpython-hardware-lis3dh-accelerometer/software

"""
import argparse
import zipfile
import os
import sys
import subprocess
import urllib.request

from typing import Dict, List


# copy from the project
DEFAULT_PROJECTS_DIR = './projects'

# copy files to the usb volume
DEFAULT_CIRCUITPY_DIR = '/Volumes/CIRCUITPY'

# copy package requirements
REQUIREMENTS_FILENAME = 'requirements.txt'

# download circuit libraries for requirements
DEFAULT_DOWNLOAD_DIR = './untracked_downloads'
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


def get_project_dir(projects_dir: str, project_name: str = None):
    if project_name is None:
        project_name = input('provide project name: ')

    project_dir = os.path.join(projects_dir, project_name)
    if not os.path.isdir(project_dir):
        projects = os.listdir(projects_dir)
        raise FileNotFoundError(
            f'no project named {project_name} at {project_dir}\n'
            f'please choose from {projects}'
        )
    return project_dir


def delete_files(location: str, user_confirm: bool = True):
    print(f"""
    WARNING: About to remove files from {location} type 'n' to abort.
    """)
    for name in os.listdir(location):
        if name.startswith('.'):
            continue
        file_or_dir = os.path.join(location, name)
        if not user_confirm or yes_no_from_user(f'remove {file_or_dir}?'):
            subprocess.check_call(['rm', '-rf', file_or_dir])
        else:
            print('stopping')
            sys.exit(1)


def copy_files(source: str, destination: str = None):
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


def download(url: str, downloads_dir: str):
    output_file = os.path.join(downloads_dir, os.path.basename(url))
    urllib.request.urlretrieve(url, output_file)
    with zipfile.ZipFile(output_file) as zp:
        zp.extractall(os.path.dirname(output_file))


def download_sources(downloads_dir: str):
    if not os.path.isdir(downloads_dir):
        os.mkdir(downloads_dir)
    for name, url in DOWNLOAD_SOURCES.items():
        print(f'downloading {name} from {url}')
        download(url, downloads_dir)


def find_requirement(requirement: str, downloads_dir: str):
    for dirname in os.listdir(downloads_dir):
        dirpath = os.path.join(downloads_dir, dirname)
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


def install_requirements(
    requirements_file: str,
    requirements_index: Dict,
    requirements_cache_dir: str,
    destination_dir: str,
):
    # 1. get requirements from requirements file
    requirements = []
    if not os.path.exists(requirements_file):
        logger.debug(f'no requirements needed: {requirements_file}')
        return
    else:
        with open(requirements_file) as fp:
            for line in fp:
                package_name = line.rstrip().strip()
                if package_name == '' or package_name.startswith('#'):
                    continue
                requirements.append(package_name)

    # 1. Download anc cache requirements
    requirements_location = {}
    for package_name in requirements:
        url = requirements_index[package_name]
        package_dir = download_requirement(url, requirements_cache_dir)
        requirements_location[package_name] = package_dir

    #


parser = argparse.ArgumentParser()
parser.add_argument('project', nargs='?')
parser.add_argument(
    '-y', '--yes',
    action='store_true',
    help='Answer yes to deleting files',
)
parser.add_argument(
    '-o', '--output',
    default=DEFAULT_CIRCUITPY_DIR,
    help=f'Output directory of the circuitpy, default={DEFAULT_CIRCUITPY_DIR}'
)
parser.add_argument(
    '-p', '--projects-dir',
    default=DEFAULT_PROJECTS_DIR,
    help=f'Projects directory, default={DEFAULT_PROJECTS_DIR}'
)
parser.add_argument(
    '--downloads-dir',
    default=DEFAULT_DOWNLOAD_DIR,
    help=f'Location to download requirements, default={DEFAULT_DOWNLOAD_DIR}'
)

if __name__ == "__main__":
    pargs = parser.parse_args()
    project_name = pargs.project
    circuitpy_dir = os.path.abspath(pargs.output)
    projects_dir = pargs.projects_dir
    downloads_dir = pargs.downloads_dir
    answer_yes = pargs.yes
    user_confirm = not answer_yes


    if not os.path.isdir(circuitpy_dir):
        raise FileNotFoundError(f'Please mount circuitpy {circuitpy_dir}')

    # 1. get project directory
    project_dir = get_project_dir(projects_dir, project_name)

    # 1. delete files
    delete_files(circuitpy_dir, user_confirm=user_confirm)

    # 1. copy all files from the project to the circuitpy
    copy_files(os.path.join(project_dir, '*'), circuitpy_dir)

    # 1. get circuitpy requirements
    requirements = get_project_requirements(project_dir)
    if len(requirements) == 0:
        sys.exit(0)

    # 1. download all possible requirements locally
    if not os.path.isdir(downloads_dir):
        download_sources(downloads_dir)

    # 1. find and copy
    lib_destination = os.path.join(circuitpy_dir, 'lib')
    if not os.path.isdir(lib_destination):
        os.mkdir(lib_destination)
    for pypackage in requirements:
        pypackage_location = find_requirement(pypackage, downloads_dir)
        copy_files(pypackage_location, lib_destination + '/')
