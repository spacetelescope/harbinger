import os
from contextlib import contextmanager

@contextmanager
def pushd(newDir):
    '''Context manager function for shell-like pushd functionality

    Allows for constructs like:
    with pushd(directory):
        'code'...
    When 'code' is finished, the working directory is restored to what it
    was when pushd was invoked.'''
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)
