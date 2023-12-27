import os

BASE_LOCATION = os.getcwd()

TEMPLATE_PATH_KEY = "template_path"
TEMPLATE_PATH = BASE_LOCATION + "\\app\\templates"

STATIC_URL = "/static/(.*)"
STATIC_PATH = BASE_LOCATION + "\\app\static"

CONFIG_PATH = BASE_LOCATION + "\config"
CONFIG_FILE_NAME = "config.json"