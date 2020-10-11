#!env python
""" Uses watchdog to update files in the circuit directory

"""
import argparse
import datetime
import logging
import os
import sys
import subprocess
import time

try:
    from watchdog.observers import Observer
except ImportError:
    raise ImportError('Need to install `pip install watchdog`')


DEFAULT_PROJECTS_DIR = './projects'
DEFAULT_CIRCUITPY_DIR = '/Volumes/CIRCUITPY'


logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser()
parser.add_argument('project', nargs='?')
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


def check_directory_exists(directory: str):
    """ Check if directory exists """
    if not os.path.isdir(directory):
        raise FileNotFoundError('no directory {}'.format(directory))


class Handler:
    """ When a file is updated, handle coping that file to the destination

    """
    def __init__(
            self,
            to_dir: str,
            update_min_seconds: int = 5,
    ):
        check_directory_exists(to_dir)
        self.to_dir = to_dir
        self.last_update_at = time.time()
        self.update_min_seconds = update_min_seconds
        logger.info('copy_to: {}'.format(self.to_dir))

    def send_file(self, filepath: str):
        cmd = [
            'cp', '-rp',
            filepath,
            os.path.abspath(self.to_dir),
        ]
        logger.info(' '.join(cmd))
        subprocess.check_call(cmd)

    def dispatch(self, event):
        t1 = time.time()
        if (t1 - self.last_update_at) < self.update_min_seconds:
            return
        if event.is_directory:
            return
        self.send_file(event.src_path)


def watch_directory(
        directory_to_watch: str,
        handler: Handler,
        dt: int = 5
    ):
    """ Start watching directory using handler 
    
    Parameters
        directory_to_watch: The directory to watch for content changes
        handler: Handler to handle file changes
        dt: Time in seconds to check the directory for changes
    """
    check_directory_exists(directory_to_watch)
    logger.info('Watching: {}'.format(directory_to_watch))
    observer = Observer()
    observer.schedule(
        handler,
        directory_to_watch,
        recursive=True,
    )
    try:
        observer.start()
        while True:
            pass
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    # Get parameters from default or command line
    pargs = parser.parse_args()
    project_name = pargs.project
    circuitpy_dir = os.path.abspath(pargs.output)
    projects_dir = pargs.projects_dir

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # 1. get project directory
    project_dir = get_project_dir(projects_dir, project_name)

    # 1. watch for updates 
    watch_directory(
        directory_to_watch=project_dir,
        handler=Handler(circuitpy_dir),
    )
