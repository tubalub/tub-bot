import os

import yaml

# Get the directory of the current script
script_dir = os.path.dirname(__file__)
config_path = os.path.join(script_dir, "config.yaml")
logging_path = os.path.join(script_dir, "logging_config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

with open(logging_path, 'r') as file:
    logging_config = yaml.safe_load(file.read())
