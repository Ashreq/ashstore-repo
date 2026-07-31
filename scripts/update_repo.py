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

from screenshot_manager import (
    save_screenshots,
    get_screenshot_urls
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


    bundle = info["bundleIdentifier"]


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


    screenshots = save_screenshots(
        info["appPath"],
        bundle
    )


    screenshot_urls = get_screenshot_urls(
        screenshots,
        REPO
    )


    sha256 = calculate_sha256(
        ipa_path
    )


    custom = get_app_config(
        bundle
    )


    app = find_app(
        repository,
        bundle
    )


    version_entry = build_version_entry(
        info,
        asset,
        release_notes,
        sha256
    )


    developer_name = custom.get(
        "developerName",
        info.get(
            "developerName",
            "Unknown"
        )
    )


    app_data = {

        "name":
            custom.get(
                "name",
                info["name"]
            ),

        "bundleIdentifier":
            bundle,

        "developerName":
            developer_name,

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
            ),

        "screenshots":
            screenshot_urls
    }



    if app:

        versions = app.get(
            "versions",
            []
        )


        versions.insert(
            0,
            version_entry
        )


        app["versions"] = versions


        update_app(
            app,
            app_data
        )


    else:


        app_data.update({

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

            "versions":
                [
                    version_entry
                ]
        })


        create_app(
            repository,
            app_data
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
