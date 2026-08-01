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
    get_app_config,
    find_app,
    create_app,
    update_app,
    sort_apps,
    trim_versions,
    load_config
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
            datetime.utcnow().strftime(
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


    icon_file = None


    icon = find_icon(
        info["appPath"],
        info["plist"]
    )


    if icon:

        icon_file = save_icon(
            icon,
            bundle
        )


    sha256 = calculate_sha256(
        ipa_path
    )


    mod_name = ""

custom = get_app_config(
    bundle,
    mod_name
)

mod_name = custom.get(
    "modName",
    ""
)

cracked_by = custom.get(
    "crackedBy",
    ""
)


    app = find_app(
    repository,
    bundle,
    mod_name
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


        update_app(
    app,
    {
        "name":
            custom.get(
                "name",
                info["name"]
            ),

        "modName":
            mod_name,

        "crackedBy":
            cracked_by,

                "bundleIdentifier":
                    bundle,

                "version":
                    info["version"],

                "versionDate":
                    datetime.utcnow().strftime(
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

                "iconURL":
                    get_icon_url(
                        icon_file,
                        REPO
                    )
            }
        )


    else:


        new_app = {

    "name":
        custom.get(
            "name",
            info["name"]
        ),

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
                datetime.utcnow().strftime(
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


    for app in repository["apps"]:

        trim_versions(
            app,
            limit
        )


    save_repository(
        repository
    )


    print(
        "AshStore update completed"
    )



if __name__ == "__main__":

    main()
