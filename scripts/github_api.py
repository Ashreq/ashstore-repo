import os
import requests
import tempfile


REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]


HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}



def github_get(url):

    response = requests.get(
        url,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.json()



def get_latest_release():

    url = (
        f"https://api.github.com/repos/"
        f"{REPO}/releases/latest"
    )

    return github_get(url)

def get_all_releases():

    url = (
        f"https://api.github.com/repos/"
        f"{REPO}/releases"
    )

    releases = github_get(utl)
    
    return [
        release
        for release in releases
        if not release.get("draft",False)
    ]

def get_release_notes(release):

    return release.get(
        "body",
        ""
    )



def get_ipa_assets(release):

    ipa_files = []


    for asset in release.get(
        "assets",
        []
    ):

        if asset["name"].lower().endswith(".ipa"):

            ipa_files.append(asset)


    return ipa_files



def download_asset(asset):

    response = requests.get(
        asset["browser_download_url"]
    )

    response.raise_for_status()


    temp = tempfile.NamedTemporaryFile(
        suffix=".ipa",
        delete=False
    )


    temp.write(
        response.content
    )

    temp.close()


    return temp.name
