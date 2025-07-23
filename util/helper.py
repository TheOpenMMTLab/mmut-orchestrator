import re
import os
import uuid


def to_valid_container_name(name: str) -> str:
    """Convert a name to a valid Docker container name."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '-', name).lower()


def get_mmut_dir():
    """List all MMUT files in the current directory."""
    # Ordner, in dem sich die aktuelle Datei befindet
    util_dir = os.path.dirname(os.path.abspath(__file__))

    # Auflösung des relativen Pfads zu einem absoluten Pfad
    return os.path.abspath(os.path.join(util_dir, '../mmut'))

def is_valid_uuid(val, version=4):
    try:
        uuid_obj = uuid.UUID(val, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == val.lower()