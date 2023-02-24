#!/usr/bin/python3

import os
import shutil

home_directory = os.path.expanduser( '~' )
env_file_path = "/Volumes/jobs02/Repositories/ftrack_utils/environment.plist"
target_path = os.path.join(home_directory, "Library", "LaunchAgents", "environment.plist")

shutil.copyfile(env_file_path, target_path)