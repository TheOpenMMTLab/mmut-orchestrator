import argparse
from util.trigger_process import trigger_process

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run docker flow for a given UUID.")
    parser.add_argument("uuid", type=str, help="UUID for the transformation run")
    args = parser.parse_args()

    trigger_process(args.uuid)
