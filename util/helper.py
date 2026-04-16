import re
import os
import yaml


def to_valid_container_name(name: str) -> str:
    """Convert a name to a valid Docker container name."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '-', name).lower()


def _mkdir(path):
    try:
        os.mkdir(path)
        os.chmod(path, 0o777)
    except FileExistsError:
        pass


def get_shared(key: str, flow_run_name: str):
    """Get a shared configuration value."""
    util_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(util_dir, '../config'))
    with open(os.path.join(config_path, 'shared.yaml'), 'r') as file:
        config = yaml.safe_load(file)

    root_path = config['root_path']
    local_path = config['local_path']
    shared_paths = config.get('shared_paths', [])

    # Create local_path/flow_run_name directory
    run_dir_name = f"flow-{flow_run_name}"
    run_dir = os.path.join(local_path, run_dir_name)
    _mkdir(run_dir)

    for shared in shared_paths:
        if shared['key'] == key:
            key_dir = os.path.join(run_dir, key)
            _mkdir(key_dir)
            for folder in (shared.get('folder') or []):
                _mkdir(os.path.join(key_dir, folder))
            break

    return os.path.join(root_path, local_path, run_dir_name, key)
