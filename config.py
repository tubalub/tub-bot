import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

with open('logging_config.yaml', 'r') as file:
    logging_config = yaml.safe_load(file.read())
