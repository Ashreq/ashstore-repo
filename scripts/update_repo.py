import os
import json
import zipfile
import plistlib
import tempfile
import requests
import shutil
from datetime import datetime


REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]

JSON_FILE = "apps.json"
ICON_FOLDER = "icons"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}


def github_api(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_latest_release():
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    return github_api(url)


def clean_release_notes(notes):

    if not notes:
        return "No release notes available"

    return notes.strip()



def download_file(url, path):

    response = requests.get(url)
    response.raise_for_status()

    with open(path, "wb") as file:
        file.write(response.content)



def extract_ipa(ipa_path):

    temp = tempfile.mkdtemp()

    with zipfile.ZipFile(ipa_path, "r") as zip_file:
        zip_file.extractall(temp)


    payload = os.path.join(
        temp,
        "Payload"
    )

    app_path = None


    for item in os.listdir(payload):

        if item.endswith(".app"):

            app_path = os.path.join(
                payload,
                item
            )

            break


    if not app_path:
        raise Exception(
            "Application bundle not found"
        )


    plist_path = os.path.join(
        app_path,
        "Info.plist"
    )


    with open(plist_path, "rb") as file:

        plist = plistlib.load(file)


    return temp, app_path, plist



def find_icon(app_path, plist):

    icons = []


    bundle_icons = plist.get(
        "CFBundleIcons",
        {}
    )


    primary = bundle_icons.get(
        "CFBundlePrimaryIcon",
        {}
    )


    icons.extend(
        primary.get(
            "CFBundleIconFiles",
            []
        )
    )


    icons.extend(
        plist.get(
            "CFBundleIconFiles",
            []
        )
    )


    icons.extend([
        "AppIcon60x60@3x.png",
        "AppIcon60x60@2x.png",
        "Icon.png"
    ])


    files = os.listdir(app_path)


    for icon in icons:

        name = icon.replace(
            ".png",
            ""
        )


        for file in files:

            if file.startswith(name):

                return os.path.join(
                    app_path,
                    file
                )


    return None



def save_icon(icon_path, bundle):

    os.makedirs(
        ICON_FOLDER,
        exist_ok=True
    )


    filename = (
        bundle.replace(".", "_")
        +
        ".png"
    )


    destination = os.path.join(
        ICON_FOLDER,
        filename
    )


    shutil.copy(
        icon_path,
        destination
    )


    return filename



def icon_url(filename):

    return (
        f"https://raw.githubusercontent.com/"
        f"{REPO}/main/icons/{filename}"
    )



def load_json():

    with open(JSON_FILE, "r") as file:

        return json.load(file)



def save_json(data):

    with open(JSON_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )



def update_existing_app(
        apps,
        plist,
        asset,
        icon,
        notes
):

    bundle = plist[
        "CFBundleIdentifier"
    ]


    version = plist.get(
        "CFBundleShortVersionString",
        "0.0.0"
    )


    today = datetime.utcnow().strftime(
        "%Y-%m-%d"
    )


    for app in apps:


        if app["bundleIdentifier"] == bundle:


            app["version"] = version

            app["versionDate"] = today

            app["versionDescription"] = notes

            app["downloadURL"] = (
                asset["browser_download_url"]
            )

            app["size"] = asset["size"]


            if icon:

                app["iconURL"] = icon_url(
                    icon
                )


            versions = app.get(
                "versions",
                []
            )


            found = False


            for item in versions:

                if item["version"] == version:

                    item["date"] = today

                    item["downloadURL"] = (
                        asset["browser_download_url"]
                    )

                    item["size"] = asset["size"]

                    item["description"] = notes

                    found = True



            if not found:

                versions.insert(
                    0,
                    {
                        "version": version,
                        "date": today,
                        "downloadURL":
                            asset["browser_download_url"],
                        "size":
                            asset["size"],
                        "description": notes
                    }
                )


            app["versions"] = versions


            print(
                f"Updated {app['name']} {version}"
            )


            return True


    return False



def create_new_app(
        apps,
        plist,
        asset,
        icon,
        notes
):

    bundle = plist[
        "CFBundleIdentifier"
    ]


    name = plist.get(
        "CFBundleDisplayName",
        plist.get(
            "CFBundleName",
            "Unknown App"
        )
    )


    version = plist.get(
        "CFBundleShortVersionString",
        "1.0.0"
    )


    today = datetime.utcnow().strftime(
        "%Y-%m-%d"
    )


    app = {

        "name": name,

        "bundleIdentifier": bundle,

        "developerName": "Unknown",

        "version": version,

        "versionDate": today,

        "versionDescription": notes,

        "downloadURL":
            asset["browser_download_url"],

        "localizedDescription":
            f"{name} application",

        "size":
            asset["size"],

        "versions": [

            {
                "version": version,
                "date": today,
                "downloadURL":
                    asset["browser_download_url"],
                "size":
                    asset["size"],
                "description":
                    notes
            }

        ]
    }


    if icon:

        app["iconURL"] = icon_url(
            icon
        )


    apps.append(app)


    print(
        f"Created new app {name}"
    )



def main():

    release = get_latest_release()


    notes = clean_release_notes(
        release.get("body", "")
    )


    ipa_asset = None


    for asset in release["assets"]:

        if asset["name"].lower().endswith(".ipa"):

            ipa_asset = asset
            break


    if not ipa_asset:

        raise Exception(
            "No IPA found"
        )


    with tempfile.NamedTemporaryFile(
        suffix=".ipa"
    ) as ipa:


        download_file(
            ipa_asset["browser_download_url"],
            ipa.name
        )


        temp, app_path, plist = extract_ipa(
            ipa.name
        )


        icon_file = None


        icon = find_icon(
            app_path,
            plist
        )


        if icon:

            icon_file = save_icon(
                icon,
                plist["CFBundleIdentifier"]
            )


    repo = load_json()


    updated = update_existing_app(
        repo["apps"],
        plist,
        ipa_asset,
        icon_file,
        notes
    )


    if not updated:

        create_new_app(
            repo["apps"],
            plist,
            ipa_asset,
            icon_file,
            notes
        )


    save_json(repo)



if __name__ == "__main__":
    main()
