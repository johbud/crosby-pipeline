# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack


import os
import sys
import subprocess
import re
import shutil

from pkg_resources import parse_version
import pip

from setuptools import setup, find_packages, Command


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
BUILD_PATH = os.path.join(ROOT_PATH, 'build')
SOURCE_PATH = os.path.join(ROOT_PATH, 'source')
README_PATH = os.path.join(ROOT_PATH, 'README.rst')
RESOURCE_PATH = os.path.join(ROOT_PATH, 'resource')
HOOK_PATH = os.path.join(RESOURCE_PATH, 'hook')
ICONS_PATH = os.path.join(RESOURCE_PATH, 'icons')

# Read version from source.
with open(
    os.path.join(SOURCE_PATH, 'open-folder', '_version.py')
) as _version_file:
    VERSION = re.match(
        r'.*__version__ = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)


STAGING_PATH = os.path.join(
    BUILD_PATH, 'open-folder-{0}'.format(VERSION)
)


class BuildPlugin(Command):
    '''Build plugin.'''

    description = 'Download dependencies and build plugin .'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Run the build step.'''
        # Clean staging path
        shutil.rmtree(STAGING_PATH, ignore_errors=True)

        # Copy hook files
        shutil.copytree(HOOK_PATH, os.path.join(STAGING_PATH, 'hook'))

        # Copy icons files
        shutil.copytree(ICONS_PATH, os.path.join(STAGING_PATH, 'icons'))

        subprocess.check_call(
            [
                sys.executable,
                '-m',
                'pip',
                'install',
                '.',
                '--target',
                os.path.join(STAGING_PATH, 'dependencies'),
            ]
        )

        result_path = shutil.make_archive(
            os.path.join(BUILD_PATH, 'open-folder-{0}'.format(VERSION)),
            'zip',
            STAGING_PATH,
        )


# Call main setup.
setup(
    name='crosby-open-folder',
    version=VERSION,
    description='Open a folder for the selected task or project.',
    long_description=open(README_PATH).read(),
    keywords='ftrack, integration, connect, location, structure',
    url='',
    author='John Buddee',
    author_email='',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={'': 'source'},
    install_requires=['ftrack-action-handler', 'show-in-file-manager'],
    tests_require=[],
    zip_safe=False,
    cmdclass={
        'build_plugin': BuildPlugin,
    },
    python_requires='>=3, < 4.0',
)
