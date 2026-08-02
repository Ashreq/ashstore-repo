import json
import os


APPS_FILE = "apps.json"
CONFIG_FILE = "app_config.json"


def load_config():

    if not os.path.exists(CONFIG_FILE):

        return {
            "settings": {
                "autoCreateApps": True,
                "versionHistoryLimit": 0,
                "sortApps": True
            },
            "apps": {}
        }


    with open(CONFIG_FILE, "r") as file:

        return json.load(file)



def save_config(data):

    with open(CONFIG_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )



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

        data = json.load(file)


    migrate_variant_ids(data)

    remove_version_history(data)


    return data



def save_repository(data):

    remove_version_history(data)

    with open(APPS_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )



def create_default_config(
        config,
        info,
        mod_name=""
):

    bundle_id = info.get(
        "bundleIdentifier",
        ""
    )


    if not bundle_id:

        return {}


    apps = config.setdefault(
        "apps",
        {}
    )


    app_name = info.get(
        "name",
        ""
    ).strip()


    variant_id = app_name.lower().replace(
        " ",
        "_"
    ).replace(
        "-",
        "_"
    )


    key = f"{bundle_id}_{variant_id}"


    if key not in apps:

        apps[key] = {

            "name":
                info.get(
                    "name",
                    ""
                ),

            "variantID":
                variant_id,

            "modName":
                mod_name,

            "crackedBy":
                "",

            "developerName":
                info.get(
                    "developerName",
                    "Unknown"
                ),

            "category":
                "Other",

            "localizedDescription":
                "",

            "featured":
                False
        }


    return apps[key]



def get_app_config(bundle_id, mod_name=""):

    config = load_config()

    apps = config.get(
        "apps",
        {}
    )


    if mod_name:

        key = f"{bundle_id}_{mod_name}"

        if key in apps:

            return apps[key]


    return apps.get(
        bundle_id,
        {}
    )



def migrate_variant_ids(repository):

    for app in repository.get(
        "apps",
        []
    ):

        if not app.get("variantID"):

            mod_name = app.get(
                "modName",
                ""
            )


            if mod_name:

                app["variantID"] = mod_name.lower().replace(
                    " ",
                    "_"
                )

            else:

                app["variantID"] = app.get(
                    "bundleIdentifier",
                    ""
                ).replace(
                    ".",
                    "_"
                )



def get_variant_id(app):

    if app.get("variantID"):

        return app["variantID"]


    if app.get("modName"):

        return app["modName"].lower().replace(
            " ",
            "_"
        )


    return app.get(
        "bundleIdentifier",
        ""
    ).replace(
        ".",
        "_"
    )



def find_app(repository, bundle_id, variant_id=""):

    migrate_variant_ids(
        repository
    )


    for app in repository.get(
        "apps",
        []
    ):

        if (
            app.get("bundleIdentifier") == bundle_id
            and
            get_variant_id(app) == variant_id
        ):

            return app


    return None



def create_app(repository, app_data):

    repository.setdefault(
        "apps",
        []
    ).append(
        app_data
    )



def update_app(app, updates):

    for key, value in updates.items():

        if value is not None:

            app[key] = value



def remove_version_history(repository):

    for app in repository.get(
        "apps",
        []
    ):

        if "versions" in app:

            del app["versions"]

def remove_empty_variants(repository):
    return



def sort_apps(repository):

    repository["apps"] = sorted(
        repository.get(
            "apps",
            []
        ),
        key=lambda x:
        (
            x.get("name","")
            +
            x.get("variantID","")
        ).lower()
    )
