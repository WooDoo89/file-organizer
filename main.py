import json
import os
import shutil
import time
from os.path import exists
from typing import Dict, List

from jsonschema import validate
from jsonschema.exceptions import ValidationError


def read_conf():
    conf = "config.json"
    if not exists(conf):
        raise FileNotFoundError(
            f"Config File does not exists. It should be in the root folder by the name '{conf}'"
        )
    with open(conf, "r") as json_data:
        return json.loads(json_data.read())


def validate_json(json_data: Dict):
    schema = {
        "type": "object",
        "properties": {
            "other_name": {"type": "string"},
            "directory": {"type": "string"},
            "categories": {
                "type": "object",
                "patternProperties": {
                    ".*": {"type": "array", "items": {"type": "string"}}
                },
            },
        },
        "required": ["categories", "other_name", "directory"],
    }
    try:
        validate(instance=json_data, schema=schema)
    except ValidationError as err:
        # TODO Change the ERROR displaying
        print(f"Validation Error in config - {err}")


def create_folders(parent_dir: str, folders: List):
    for folder_name in folders:
        folder_path = os.path.join(parent_dir, folder_name)
        try:
            os.mkdir(folder_path)
            print(f"Folder {folder_path} created!")
        except FileExistsError:
            print(f"WARNING: Folder {folder_path} already exists")


def organize_files(json_data: Dict):
    parent_dir = json_data["directory"]

    for filename in os.listdir(parent_dir):
        full_path = os.path.join(parent_dir, filename)
        if os.path.isfile(full_path):
            target_dir = next(
                (
                    os.path.join(parent_dir, key)
                    for key, value in json_data["categories"].items()
                    if os.path.splitext(full_path)[1] in value
                ),
                None,
            )
            if not target_dir:
                target_dir = os.path.join(parent_dir, json_data["other_name"])
            shutil.move(full_path, target_dir)
            # print(f"File {full_path} was moved to {target_dir}")


if __name__ == "__main__":
    start_time = time.time()
    data = read_conf()
    print("--- %s seconds | READ CONF ---" % (time.time() - start_time))
    validate_json(data)
    print("--- %s seconds | VALIDATE DATA ---" % (time.time() - start_time))
    categories, other_name, directory = (
        data["categories"],
        data["other_name"],
        data["directory"],
    )
    create_folders(directory, list(categories.keys()) + [other_name])
    print("--- %s seconds | CREATE FOLDERS ---" % (time.time() - start_time))
    organize_files(data)
    print("--- %s seconds | MOVE EVERYTHING ---" % (time.time() - start_time))
