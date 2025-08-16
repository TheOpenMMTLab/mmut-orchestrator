import argparse
from util.docker_flow import docker_flow

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run docker flow for a given UUID.")
    parser.add_argument("uuid", type=str, help="UUID for the transformation run")
    args = parser.parse_args()

    docker_flow(args.uuid)
