import os
import json
import zipfile
import plistlib
import tempfile
import requests
from datetime import datetime


REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]

JSON_FILE = "apps.json"


HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}


def github_api(url):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def get_latest_release():

    url = f"https://api.github.com/repos/{REPO}/releases/latest"

    return github_api(url)


def download_file(url, path):

    r = requests.get(url)

    r.raise_for_status()

    with open(path, "wb") as f:
        f.write(r.content)


def extract_info_plist(ipa):

    temp = tempfile.mkdtemp()

    with zipfile.ZipFile(ipa, "r") as z:
        z.extractall(temp)

    payload = os.path.join(temp, "Payload")

    app_folder = None

    for item in os.listdir(payload):
        if item.endswith(".app"):
            app_folder = os.path.join(payload, item)
            break

    if not app_folder:
        raise Exception("App folder not found")

    plist_path = os.path.join(
        app_folder,
        "Info.plist"
    )

    with open(plist_path, "rb") as f:
        return plistlib.load(f)


def load_json():

    with open(JSON_FILE, "r") as f:
        return json.load(f)


def save_json(data):

    with open(JSON_FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def update_app(repo, plist, asset):

    bundle = plist.get(
        "CFBundleIdentifier"
    )

    version = plist.get(
        "CFBundleShortVersionString",
        "0.0.0"
    )

    build = plist.get(
        "CFBundleVersion",
        ""
    )


    today = datetime.utcnow().strftime(
        "%Y-%m-%d"
    )


    for app in repo["apps"]:

        if app["bundleIdentifier"] == bundle:

            download = asset["browser_download_url"]

            size = asset["size"]


            app["version"] = version

            app["versionDate"] = today

            app["versionDescription"] = (
                f"Version {version} release"
            )

            app["downloadURL"] = download

            app["size"] = size


            history = app.get(
                "versions",
                []
            )


            exists = False


            for item in history:

                if item["version"] == version:

                    item["date"] = today
                    item["downloadURL"] = download
                    item["size"] = size
                    item["description"] = (
                        f"Version {version} release"
                    )

                    exists = True


            if not exists:

                history.insert(
                    0,
                    {
                        "version": version,
                        "date": today,
                        "downloadURL": download,
                        "size": size,
                        "description":
                            f"Version {version} release"
                    }
                )


            app["versions"] = history


            print(
                f"Updated {app['name']} to {version}"
            )

            return True


    print(
        f"No matching app found for {bundle}"
    )

    return False



def main():

    release = get_latest_release()

    assets = release["assets"]


    ipa_asset = None


    for asset in assets:

        if asset["name"].lower().endswith(".ipa"):

            ipa_asset = asset

            break


    if not ipa_asset:

        raise Exception(
            "No IPA found in release"
        )


    with tempfile.NamedTemporaryFile(
        suffix=".ipa"
    ) as f:


        download_file(
            ipa_asset["browser_download_url"],
            f.name
        )


        plist = extract_info_plist(
            f.name
        )


    repo = load_json()


    changed = update_app(
        repo,
        plist,
        ipa_asset
    )


    if changed:

        save_json(repo)



if __name__ == "__main__":
    main()