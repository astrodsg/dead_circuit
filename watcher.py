#!env python
""" Uses watchdog to update files in the circuit directory

"""
import os
import sys
import subprocess
import time
import logging
from watchdog.observers import Observer


PROJECTS_DIR = './projects'
CIRCUITPYTHON_DIR = '/Volumes/CIRCUITPY'


# ######################################################### #


logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


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


def check_directory_exists(directory):
    """ Check if directory exists """
    if not os.path.isdir(directory):
        raise FileNotFoundError('no directory {}'.format(directory))


class Handler:
    """ When a file is updated, handle coping that file to the destination

    """
    def __init__(self, to_dir):
        check_directory_exists(to_dir)
        self.to_dir = to_dir
        logger.info('copy_to: {}'.format(self.to_dir))

    def send_file(self, file):
        cmd = ' '.join([
            'cp', '-rp',
            file,
            os.path.abspath(self.to_dir),
        ])
        logger.info(cmd)
        status, msg = subprocess.getstatusoutput(cmd)
        if status != 0:
            raise IOError(msg)

    def dispatch(self, event):
        if event.is_directory:
            return
        self.send_file(event.src_path)


def watch_directory(directory_to_watch, handler, dt=5):
    check_directory_exists(directory_to_watch)
    logger.info('watching: {}'.format(directory_to_watch))
    observer = Observer()
    observer.schedule(
        handler,
        directory_to_watch,
        recursive=True,
    )
    observer.start()
    try:
        while True:
            time.sleep(dt)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    project_dir = get_project_from_user()
    handler = Handler(CIRCUITPYTHON_DIR)
    watch_directory(
        directory_to_watch=project_dir,
        handler=handler,
    )
