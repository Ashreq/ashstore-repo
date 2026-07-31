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


def download_file(url, path):

    r = requests.get(url)
    r.raise_for_status()

    with open(path, "wb") as f:
        f.write(r.content)


def extract_ipa(ipa_path):

    temp = tempfile.mkdtemp()

    with zipfile.ZipFile(ipa_path, "r") as z:
        z.extractall(temp)

    payload = os.path.join(temp, "Payload")

    app_path = None

    for item in os.listdir(payload):

        if item.endswith(".app"):

            app_path = os.path.join(
                payload,
                item
            )

            break

    if not app_path:
        raise Exception("App bundle not found")

    plist_path = os.path.join(
        app_path,
        "Info.plist"
    )

    with open(plist_path, "rb") as f:
        plist = plistlib.load(f)


    return temp, app_path, plist



def find_icon(app_path, plist):

    possible_icons = []


    # Modern iOS apps

    icons = plist.get(
        "CFBundleIcons",
        {}
    )


    primary = icons.get(
        "CFBundlePrimaryIcon",
        {}
    )


    possible_icons.extend(
        primary.get(
            "CFBundleIconFiles",
            []
        )
    )


    # Older apps

    possible_icons.extend(
        plist.get(
            "CFBundleIconFiles",
            []
        )
    )


    # Add common names

    possible_icons.extend([
        "AppIcon60x60@2x.png",
        "AppIcon60x60@3x.png",
        "Icon.png"
    ])


    for icon in possible_icons:

        for file in os.listdir(app_path):

            if file.startswith(icon.replace(".png","")):

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
        bundle.replace(".","_")
        + ".png"
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



def load_json():

    with open(JSON_FILE,"r") as f:

        return json.load(f)



def save_json(data):

    with open(JSON_FILE,"w") as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )



def icon_url(filename):

    return (
        f"https://raw.githubusercontent.com/"
        f"{REPO}/main/icons/{filename}"
    )



def update_existing_app(
        apps,
        plist,
        asset,
        icon
):

    bundle = plist["CFBundleIdentifier"]

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

            app["versionDescription"] = (
                f"Version {version} release"
            )

            app["downloadURL"] = (
                asset["browser_download_url"]
            )

            app["size"] = asset["size"]


            if icon:

                app["iconURL"] = icon_url(
                    icon
                )


            history = app.get(
                "versions",
                []
            )


            found = False


            for item in history:

                if item["version"] == version:

                    item["date"] = today
                    item["downloadURL"] = asset[
                        "browser_download_url"
                    ]

                    item["size"] = asset["size"]

                    found = True


            if not found:

                history.insert(
                    0,
                    {
                        "version": version,
                        "date": today,
                        "downloadURL":
                            asset[
                            "browser_download_url"
                            ],
                        "size":
                            asset["size"],
                        "description":
                            f"Version {version} release"
                    }
                )


            app["versions"] = history


            print(
                "Updated:",
                app["name"]
            )

            return True


    return False



def create_new_app(
        apps,
        plist,
        asset,
        icon
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


    new_app = {

        "name": name,

        "bundleIdentifier": bundle,

        "developerName": "Unknown",

        "version": version,

        "versionDate":
            datetime.utcnow().strftime(
                "%Y-%m-%d"
            ),

        "versionDescription":
            f"Version {version} release",

        "downloadURL":
            asset["browser_download_url"],

        "localizedDescription":
            f"{name} application",

        "size":
            asset["size"],

        "versions":[

            {
                "version":version,
                "date":
                    datetime.utcnow().strftime(
                    "%Y-%m-%d"
                    ),

                "downloadURL":
                    asset[
                    "browser_download_url"
                    ],

                "size":
                    asset["size"],

                "description":
                    f"Version {version} release"
            }

        ]
    }


    if icon:

        new_app["iconURL"] = icon_url(
            icon
        )


    apps.append(new_app)


    print(
        "Created new app:",
        name
    )


    return True



def main():

    release = get_latest_release()


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
            ipa_asset[
                "browser_download_url"
            ],
            ipa.name
        )


        temp, app_path, plist = extract_ipa(
            ipa.name
        )


        icon = find_icon(
            app_path,
            plist
        )


        icon_file = None


        if icon:

            icon_file = save_icon(
                icon,
                plist[
                    "CFBundleIdentifier"
                ]
            )


    repo = load_json()


    updated = update_existing_app(
        repo["apps"],
        plist,
        ipa_asset,
        icon_file
    )


    if not updated:

        create_new_app(
            repo["apps"],
            plist,
            ipa_asset,
            icon_file
        )


    save_json(repo)



if __name__ == "__main__":
    main()
