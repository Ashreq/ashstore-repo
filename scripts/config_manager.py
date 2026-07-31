import json
import os


CONFIG_FILE = "app_config.json"


def load_config():

    if not os.path.exists(CONFIG_FILE):
        return {}

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)



def save_config(config):

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            indent=2,
            ensure_ascii=False
        )



def update_app_config(
    bundle_id,
    name,
    developer,
    description="",
    category="Other"
):

    config = load_config()


    if bundle_id not in config:

        config[bundle_id] = {

            "name": name,

            "developerName": developer,

            "description": description,

            "category": category

        }


    else:

        # Update only empty fields
        if not config[bundle_id].get("name"):
            config[bundle_id]["name"] = name

        if not config[bundle_id].get("developerName"):
            config[bundle_id]["developerName"] = developer


    save_config(config)


    return config[bundle_id]
