import os
import hashlib
from datetime import datetime

from github_api import (
    get_latest_release,
    get_release_notes,
    get_ipa_assets,
    download_asset
)

from ipa_reader import (
    read_ipa_info
)

from icon_manager import (
    find_icon,
    save_icon,
    get_icon_url
)

from repository import (
    load_repository,
    save_repository,
    find_app,
    create_app,
    update_app,
    sort_apps,
    trim_versions,
    load_config,
    save_config,
    version_exists,
    remove_empty_variants,
    create_default_config,
    migrate_variant_ids
)


REPO = os.environ["GITHUB_REPOSITORY"]


def calculate_sha256(file_path):

    sha = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(4096),
            b""
        ):

            sha.update(chunk)

    return sha.hexdigest()



def detect_mod_name(asset_name, bundle, config):

    name = asset_name.lower()

    apps_config = config.get(
        "apps",
        {}
    )

    for key, value in apps_config.items():

        if key.startswith(bundle + "_"):

            possible_mod = value.get(
                "modName",
                ""
            )

            if possible_mod.lower().replace(
                " ",
                "_"
            ) in name:

                return possible_mod

    return ""



def get_variant_config(config, bundle, mod_name=""):

    apps_config = config.get(
        "apps",
        {}
    )

    if mod_name:

        key = f"{bundle}_{mod_name}"

        if key in apps_config:

            return apps_config[key]


    return apps_config.get(
        bundle,
        {}
    )



def get_variant_id(custom, mod_name=""):

    variant_id = custom.get(
        "variantID",
        ""
    )

    if variant_id:

        return variant_id


    if mod_name:

        return mod_name.lower().replace(
            " ",
            "_"
        )


    return ""



def build_version_entry(
        info,
        asset,
        notes,
        sha256
):

    return {

        "version":
            info["version"],

        "date":
            datetime.now().strftime(
                "%Y-%m-%d"
            ),

        "downloadURL":
            asset["browser_download_url"],

        "size":
            asset["size"],

        "sha256":
            sha256,

        "description":
            notes
    }



def process_app(
        asset,
        release_notes,
        repository,
        config
):

    print(
        "Processing:",
        asset["name"]
    )


    ipa_path = download_asset(
        asset
    )


    info = read_ipa_info(
        ipa_path
    )


    bundle = info[
        "bundleIdentifier"
    ]


    mod_name = detect_mod_name(
        asset["name"],
        bundle,
        config
    )


        custom = get_variant_config(
        config,
        bundle,
        mod_name
    )

    if not custom:

        custom = create_default_config(
            config,
            info,
            mod_name
        )

    save_config(
        config
    )


    variant_id = get_variant_id(
        custom,
        mod_name
    )


    cracked_by = custom.get(
        "crackedBy",
        ""
    )


    icon_file = None


    icon = find_icon(
        info["appPath"],
        info["plist"]
    )


    if icon:

        icon_name = f"{bundle}_{variant_id}".replace(
            " ",
            "_"
        )

        icon_file = save_icon(
            icon,
            icon_name
        )


    sha256 = calculate_sha256(
        ipa_path
    )


    app = find_app(
        repository,
        bundle,
        variant_id
    )


    version_entry = build_version_entry(
        info,
        asset,
        release_notes,
        sha256
    )


    if app:

        versions = app.get(
            "versions",
            []
        )


        if not version_exists(
            versions,
            version_entry
        ):

            versions.insert(
                0,
                version_entry
            )


        app["versions"] = versions


        updates = {

            "name":
                custom.get(
                    "name",
                    info["name"]
                ),

            "variantID":
                variant_id,

            "modName":
                mod_name,

            "crackedBy":
                cracked_by,

            "bundleIdentifier":
                bundle,

            "version":
                info["version"],

            "versionDate":
                datetime.now().strftime(
                    "%Y-%m-%d"
                ),

            "versionDescription":
                release_notes,

            "downloadURL":
                asset["browser_download_url"],

            "size":
                asset["size"],

            "sha256":
                sha256
        }


        if icon_file:

            updates["iconURL"] = get_icon_url(
                icon_file,
                REPO
            )


        update_app(
            app,
            updates
        )


    else:

        new_app = {

            "name":
                custom.get(
                    "name",
                    info["name"]
                ),

            "variantID":
                variant_id,

            "modName":
                mod_name,

            "crackedBy":
                cracked_by,

            "bundleIdentifier":
                bundle,

            "developerName":
                custom.get(
                    "developerName",
                    "Unknown"
                ),

            "category":
                custom.get(
                    "category",
                    ""
                ),

            "localizedDescription":
                custom.get(
                    "localizedDescription",
                    ""
                ),

            "version":
                info["version"],

            "versionDate":
                datetime.now().strftime(
                    "%Y-%m-%d"
                ),

            "versionDescription":
                release_notes,

            "downloadURL":
                asset["browser_download_url"],

            "size":
                asset["size"],

            "sha256":
                sha256,

            "versions":
                [
                    version_entry
                ]
        }


        if icon_file:

            new_app["iconURL"] = get_icon_url(
                icon_file,
                REPO
            )


        create_app(
            repository,
            new_app
        )



def main():

    print(
        "Starting AshStore v2 update"
    )

    release = get_latest_release()

    notes = get_release_notes(
        release
    )

    repository = load_repository()

    config = load_config()

    migrate_variant_ids(
        repository
    )

    assets = get_ipa_assets(
        release
    )

    for asset in assets:

        process_app(
            asset,
            notes,
            repository,
            config
        )

    settings = config.get(
        "settings",
        {}
    )

    if settings.get(
        "sortApps",
        True
    ):

        sort_apps(
            repository
        )

    limit = settings.get(
        "versionHistoryLimit",
        10
    )

    for app in repository.get(
        "apps",
        []
    ):

        trim_versions(
            app,
            limit
        )

    remove_empty_variants(
        repository
    )

    save_repository(
        repository
    )

    save_config(
        config
    )

    print(
        "AshStore update completed"
    )


if __name__ == "__main__":

    main()
