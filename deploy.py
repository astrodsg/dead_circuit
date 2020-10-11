#!env python
""" Run by parent deploy script


https://learn.adafruit.com/circuitpython-hardware-lis3dh-accelerometer/software

"""
import argparse
import logging
import os
import sys
import subprocess
from typing import Dict, List
import urllib.request
import zipfile

logger = logging.getLogger('deploy')

# copy from the project
DEFAULT_PROJECTS_DIR = './projects'

# copy files to the usb volume
DEFAULT_CIRCUITPY_DIR = '/Volumes/CIRCUITPY'

# copy package requirements
REQUIREMENTS_FILENAME = 'requirements.txt'

# download circuit libraries for requirements
DEFAULT_REQUIREMENTS_CACHE_DIR = './untracked_downloads'
REQUIREMENTS_BUNDLES = {
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
    """ Utility to get a yes/no answer from user and return boolean """
    msg = msg + ' [y/n]: '
    while True:
        user_input = input(msg)
        if user_input == 'n':
            return False
        elif user_input == 'y':
            return True
        print('enter [y]es or [n]o')


def get_project_dir(projects_dir: str, project_name: str = None):
    """ Get directory of the projecct """
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
    """ Delete files at location using `rm -rf {location}`
    """
    logger.warning(f"""

    WARNING: Removing files from '{location}'
    """)
    file_or_dir_to_remove = []
    for name in os.listdir(location):
        if name.startswith('.'):
            continue
        file_or_dir = os.path.join(location, name)
        file_or_dir_to_remove.append(file_or_dir)

    if len(file_or_dir_to_remove) > 50:
        raise Exception(
            f'Something is wrong, should not be removing '
            f'{len(file_or_dir_to_remove)} files.\n\n'
            f'{file_or_dir_to_remove}'
        )

    for file_or_dir in file_or_dir_to_remove:
        if not user_confirm or yes_no_from_user(f'remove {file_or_dir}?'):
            subprocess.check_call(['rm', '-rf', file_or_dir])
        else:
            logger.error('User requested stop')
            sys.exit(1)


def copy_files(source: str, destination: str = None):
    """ Copy files using `cp -rp {source} {destination}` 
    """
    cmd = f'cp -rp {source} {destination}'
    logger.info(cmd)
    subprocess.check_output(cmd, shell=True)


def download_zipfile(url: str, destination: str):
    """ Download a zip file and unpack it's contents into the destination """
    output_file = os.path.join(destination, os.path.basename(url))
    urllib.request.urlretrieve(url, output_file)
    with zipfile.ZipFile(output_file) as zp:
        zp.extractall(os.path.dirname(output_file))


def download_requirements_bundles(
        requirements_bundles: Dict,
        requirments_cache_dir: str = DEFAULT_REQUIREMENTS_CACHE_DIR
):
    """ Download requirements bundles and cache 
    
    Requirments bundles are collections of python modules. Download each of 
    them and then have all the modules that may be needed to select individually
    """
    if not os.path.isdir(requirments_cache_dir):
        os.mkdir(requirments_cache_dir)
    else:
        return

    for name, url in requirements_bundles.items():
        logger.debug(f'downloading {name} from {url}')
        download_zipfile(url, requirments_cache_dir)


def find_requirement_location(requirement: str, requirments_cache_dir: str):
    """ Search the bundles for a required package and return the path
    """
    for dirname in os.listdir(requirments_cache_dir):
        dirpath = os.path.join(requirments_cache_dir, dirname)
        if not os.path.isdir(dirpath):
            continue

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


def read_requirements_file(requirements_file: str):
    """ Read the requirements file and return requirements

    This reads a format similar to requirements.txt and then returns the 
    requirements.
    """
    requirements = []
    with open(requirements_file) as fp:
        for line in fp:
            package = line.rstrip().strip()
            if package == '' or package.startswith('#'):
                continue
            requirements.append(package)
    return requirements


def download_and_copy_requirements(
    requirements_file: str,
    requirements_destination: str,
    requirements_bundles: Dict = None,
    requirments_cache_dir: str = None,
):
    """ Download needed requirements and copy to desination

    Parameters
        requirments_file: Custom specification similar to requirements.txt
            that specifies individual python modules needed.
        requirements_destination: Path to copy the python modules to.
        requirments_bundles: Circuitpy has bundles of python libraries in the
            form of zip releases. These bundles contain the python modules. This
            code will download all the bundles and then search them for the
            required python module.
            
            * key: arbitrary name of the bundle
            * value: Url of the zip file for the bundle

        requirments_cache_dir: Directory to download all the 
            requirements_bundles to.
    """
    if requirements_bundles is None:
        requirements_bundles = REQUIREMENTS_BUNDLES

    # 1. check for requirements file
    if not os.path.exists(requirements_file):
        logger.debug(f'No requirements needed. {requirements_file}')
        return

    # 1. check for requirements destination
    if not os.path.isdir(requirements_destination):
        logger.debug(
            f'Creating requirements destination {requirements_destination}')
        os.mkdir(requirements_destination)

    # 1. download all requirements bundles if not already downloaded
    download_requirements_bundles(
        requirements_bundles, requirments_cache_dir)

    # 1. find and copy
    requirements = read_requirements_file(requirements_file)
    for requirement in requirements:
        package_location = find_requirement_location(
            requirement, requirments_cache_dir)
        copy_files(package_location, requirements_destination)


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
    '--requirments-cache-dir',
    default=DEFAULT_REQUIREMENTS_CACHE_DIR,
    help=(
        f'Location to download requirements bundles, '
        f'default={DEFAULT_REQUIREMENTS_CACHE_DIR}'
    )
)

if __name__ == "__main__":
    pargs = parser.parse_args()
    project_name = pargs.project
    circuitpy_dir = os.path.abspath(pargs.output)
    projects_dir = pargs.projects_dir
    requirments_cache_dir = pargs.requirments_cache_dir
    answer_yes = pargs.yes
    user_confirm = not answer_yes

    logging.basicConfig(level=logging.DEBUG)

    if not os.path.isdir(circuitpy_dir):
        raise FileNotFoundError(f'Please mount circuitpy {circuitpy_dir}')

    # 1. get project directory
    project_dir = get_project_dir(projects_dir, project_name)

    # 1. delete files
    delete_files(circuitpy_dir, user_confirm=user_confirm)

    # 1. copy all files from the project to the circuitpy
    copy_files(os.path.join(project_dir, '*'), circuitpy_dir)

    # 1. get requirements and copy them to circuitpy
    requirements_file = os.path.join(project_dir, 'requirements.txt')
    requirements_destination = os.path.join(circuitpy_dir, 'lib')
    download_and_copy_requirements(
        requirements_file,
        requirements_destination,
        requirments_cache_dir=requirments_cache_dir,
    )
