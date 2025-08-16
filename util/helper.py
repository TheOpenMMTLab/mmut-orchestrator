import re
import os
import uuid
import yaml

def to_valid_container_name(name: str) -> str:
    """Convert a name to a valid Docker container name."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '-', name).lower()





def get_shared(key : str):
    """Get a shared configuration value."""
    util_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.abspath(os.path.join(util_dir, '../config'))
    with open(os.path.join(config_path, 'shared.yaml'), 'r') as file:
        config = yaml.safe_load(file)
    return config.get(key, None)



