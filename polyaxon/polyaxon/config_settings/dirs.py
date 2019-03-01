import json
import os

from polyaxon.config_manager import config

# dirs
DIRS_NVIDIA = config.get_string('POLYAXON_DIRS_NVIDIA')
MOUNT_PATHS_NVIDIA = config.get_string('POLYAXON_MOUNT_PATHS_NVIDIA', is_optional=True)
LD_LIBRARY_PATH = config.get_string('LD_LIBRARY_PATH', is_optional=True)

DIRS_NVIDIA = json.loads(DIRS_NVIDIA) if DIRS_NVIDIA else {}
MOUNT_PATHS_NVIDIA = json.loads(MOUNT_PATHS_NVIDIA) if MOUNT_PATHS_NVIDIA else {}

if not all(list(DIRS_NVIDIA.keys())):
    DIRS_NVIDIA = {}

if not all(list(MOUNT_PATHS_NVIDIA.keys())):
    MOUNT_PATHS_NVIDIA = {}


if MOUNT_PATHS_NVIDIA:
    if 'bin' in MOUNT_PATHS_NVIDIA:
        # Update PATH with the nvidia bin
        os.environ['PATH'] = '{}:{}'.format(os.getenv('PATH', ''), MOUNT_PATHS_NVIDIA['bin'])
