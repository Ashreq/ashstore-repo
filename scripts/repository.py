import json
import os


APPS_FILE = "apps.json"
CONFIG_FILE = "app_config.json"


def load_config():

    if not os.path.exists(CONFIG_FILE):
        return {
            "settings": {},
            "apps": {}
        }

    with open(CONFIG_FILE, "r") as file:
        return json.load(file)



def load_repository():

    if not os.path.exists(APPS_FILE):

        return {
            "name": "AshStore",
            "identifier": "com.github.ashreq.ashstore-repo",
            "subtitle": "Custom apps and tweaks",
            "description": "A personal repository for enhanced applications.",
            "apps": []
        }


    with open(APPS_FILE, "r") as file:
        return json.load(file)



def save_repository(data):

    with open(APPS_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )



def get_app_config(bundle_id, mod_name=""):

    config = load_config()

    apps = config.get(
        "apps",
        {}
    )


    # New format:
    # bundleID_ModName
    config_key = bundle_id

    if mod_name:
        config_key = f"{bundle_id}_{mod_name}"


    return apps.get(
        config_key,
        {}
    )



def find_app(repository, bundle_id, mod_name=""):

    for app in repository.get("apps", []):

        if (
            app.get("bundleIdentifier") == bundle_id
            and app.get("modName", "") == mod_name
        ):
            return app


    return None



def create_app(repository, app_data):

    repository["apps"].append(
        app_data
    )



def update_app(app, updates):

    for key, value in updates.items():

        if value is not None:

            app[key] = value



def trim_versions(app, limit):

    versions = app.get(
        "versions",
        []
    )

    app["versions"] = versions[:limit]



def sort_apps(repository):

    repository["apps"] = sorted(
        repository["apps"],
        key=lambda x:
            (
                x.get(
                    "name",
                    ""
                )
                +
                x.get(
                    "modName",
                    ""
                )
            ).lower()
    )
