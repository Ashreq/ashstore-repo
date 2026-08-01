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

        data = json.load(file)

    migrate_variant_ids(data)
    merge_duplicate_apps(data)

    return data



def save_repository(data):

    merge_duplicate_apps(data)

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



def get_variant_id(app):

    if app.get("variantID"):

        return app["variantID"]


    if app.get("modName"):

        return app["modName"].lower().replace(
            " ",
            "_"
        )


    return ""



def find_app(repository, bundle_id, variant_id=""):

    migrate_variant_ids(repository)


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



def version_exists(versions, new_version):

    for version in versions:

        if (
            version.get("downloadURL")
            ==
            new_version.get("downloadURL")
        ):

            return True


    return False



def merge_duplicate_apps(repository):

    apps = repository.get(
        "apps",
        []
    )


    merged = {}


    for app in apps:

        bundle = app.get(
            "bundleIdentifier",
            ""
        )

        variant = get_variant_id(
            app
        )


        key = f"{bundle}_{variant}"


        if key not in merged:

            app["variantID"] = variant

            merged[key] = app


        else:

            existing = merged[key]


            # Merge versions

            existing_versions = existing.get(
                "versions",
                []
            )


            new_versions = app.get(
                "versions",
                []
            )


            urls = {
                v.get("downloadURL")
                for v in existing_versions
            }


            for version in new_versions:

                if version.get("downloadURL") not in urls:

                    existing_versions.append(
                        version
                    )


            existing["versions"] = existing_versions


            # Keep latest release info

            if app.get("versionDate","") >= existing.get(
                "versionDate",
                ""
            ):

                for key,value in app.items():

                    if key != "versions":

                        existing[key] = value



    repository["apps"] = list(
        merged.values()
    )



def remove_empty_variants(repository):

    merge_duplicate_apps(
        repository
    )



def trim_versions(app, limit):

    versions = app.get(
        "versions",
        []
    )


    app["versions"] = versions[:limit]



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
