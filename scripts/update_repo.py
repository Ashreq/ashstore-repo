import os
import hashlib
from datetime import datetime

from github_api import (
    get_all_releases,
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
    create_app,
    sort_apps,
    load_config,
    save_config,
    create_default_config,
    migrate_variant_ids,
    cleanup_deleted_releases
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

    import re

    filename = os.path.splitext(asset_name)[0]

    filename = filename.replace("-", "_")

    words = filename.split("_")

    bundle_name = bundle.split(".")[-1].lower()

    ignore = {
        "ipa",
        "ios",
        "unsigned",
        "signed",
        "bonus",
        "build",
        "full",
        "by",
        "ashraq",
        "official"
    }

    cleaned = []

    for word in words:

        lower = word.lower()

        if lower in ignore:
            continue

        if re.match(r"^v?\d+(\.\d+)*.*$", lower):
            continue

        cleaned.append(word)

    lower_words = [w.lower() for w in cleaned]

    app_index = -1

    for i, word in enumerate(lower_words):

        if bundle_name in word:
            app_index = i
            break

    if app_index == -1:

        return ""

    #
    # Filename starts with app name
    #
    # Example:
    # YouTube_YTKillerPlus_v21
    #

    if app_index == 0:

        variant = cleaned[1:]

    #
    # Filename ends with app name
    #
    # Example:
    # YTKACE_0.7.5_YouTube
    #

    else:

        variant = cleaned[:app_index]

    if not variant:

        return ""

    return "_".join(variant).lower()



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

    if mod_name:

        return mod_name.lower().replace(
            " ",
            "_"
        ).replace(
            "-",
            "_"
        )


    variant_id = custom.get(
        "variantID",
        ""
    )

    if variant_id:

        return variant_id


    return custom.get(
        "bundleIdentifier",
        ""
    ).replace(
        ".",
        "_"
    )

    if mod_name:

        return mod_name.lower().replace(
            " ",
            "_"
        ).replace(
            "-",
            "_"
        )


    return custom.get(
        "bundleIdentifier",
        ""
    ).replace(
        ".",
        "_"
    )


    if mod_name:

        return mod_name.lower().replace(
            " ",
            "_"
        )


    return ""



def format_mod_name(name):

    if not name:
        return ""

    known = {
        "ytkace": "YTKACE",
        "ytkillerplus": "YTKillerPlus",
        "glow": "Glow",
        "plus": "Plus",
        "nuvio": "Nuvio"
    }

    key = name.lower()

    if key in known:
        return known[key]

    return name.replace(
        "_",
        " "
    ).title()

def get_release_description(asset_name, release_notes):

    if not release_notes:
        return ""

    asset_key = asset_name.replace(
        ".ipa",
        ""
    )

    lines = release_notes.splitlines()

    found = False
    collecting = False
    description = []

    for line in lines:

        line = line.strip()

        if line == f"[{asset_key}]":
            found = True
            continue

        if found:

            if line.startswith("[") and line.endswith("]"):
                break

            if line.lower().startswith(
                "description:"
            ):
                collecting = True
                continue

            if line.lower().startswith(
                "version description:"
            ):
                break

            if collecting and line:
                description.append(line)

    return " ".join(description)

def get_version_description(asset_name, release_notes):

    if not release_notes:
        return ""

    asset_key = asset_name.replace(
        ".ipa",
        ""
    )

    lines = release_notes.splitlines()

    found = False
    collecting = False
    description = []

    for line in lines:

        line = line.strip()

        if line == f"[{asset_key}]":
            found = True
            continue

        if found:

            if line.startswith("[") and line.endswith("]"):
                break

            if line.lower().startswith(
                "version description:"
            ):
                collecting = True
                continue

            if collecting:

                if line:
                    description.append(line)

    return " ".join(description)
def clean_asset_words(asset_name):

    import re

    filename = os.path.splitext(asset_name)[0]

    filename = filename.replace("-", "_")

    words = filename.split("_")

    cleaned = []

    ignore = {
        "ipa",
        "ios",
        "unsigned",
        "signed",
        "cracked",
        "patched",
        "patch",
        "full",
        "build",
        "release",
        "beta",
        "official",
        "bonus",
        "by",
        "ashraq"
    }

    for word in words:

        lower = word.lower()

        # Remove ignored words
        if lower in ignore:
            continue

        # Remove version numbers
        if re.match(
            r"^v?\d+(\.\d+)*$",
            lower
        ):
            continue

        cleaned.append(word)

    return cleaned



def detect_app_name(asset_name, info, bundle):

    # Prefer IPA metadata
    plist_name = info.get(
        "name",
        ""
    )

    if plist_name:
        return plist_name


    # Bundle fallback

    known_apps = {

        "com.google.ios.youtube": "YouTube",

        "com.spotify.client": "Spotify",

        "com.facebook.Facebook": "Facebook",

        "com.burbn.instagram": "Instagram",

        "com.firecore.infuse": "Infuse",

    }


    if bundle in known_apps:

        return known_apps[bundle]


    # Last fallback from filename

    words = clean_asset_words(
        asset_name
    )

    if words:

        return words[0].title()


    return "Unknown"



def detect_mod_name_new(asset_name, app_name):

    words = clean_asset_words(
        asset_name
    )


    if not words:

        return ""


    app_lower = app_name.lower()


    mods = []


    for word in words:

        lower = word.lower()

        if lower == app_lower:
            continue


        mods.append(word)


    if not mods:

        return ""


    return " ".join(mods)



def build_display_name(app_name, mod_name):

    if not mod_name:
        return app_name


    mod = mod_name.lower()


    # Special replacements
    if "eeveespotify" in mod:
        return "EeveeSpotify"


    if "ytplusm" in mod:
        return f"{app_name} YTPlus M"


    if "ytplus" in mod:
        return f"{app_name} YTPlus"


    if "ytkace" in mod:
        return f"{app_name} YTKACE"


    if "glow" in mod:
        return f"{app_name} Glow"


    if "enhanced" in mod:
        return f"{app_name} Enhanced"


    if "tgextra" in mod:
        return f"{app_name} TGExtra"


    if "plus" in mod:
        return f"{app_name} Plus"


    # fallback
    clean_mod = (
        mod_name
        .replace("_", " ")
        .split()[0]
        .title()
    )


    return f"{app_name} {clean_mod}"
    
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


    app_name = detect_app_name(
        asset["name"],
        info,
        bundle
    )

    mod_name = detect_mod_name_new(
        asset["name"],
        app_name
    )

    display_name = build_display_name(
        app_name,
        mod_name
    )


    custom = get_variant_config(
        config,
        bundle,
        mod_name
    )


    if not custom:

        print(
            "CREATING NEW CONFIG:",
            bundle,
            mod_name
        )

        custom = create_default_config(
            config,
            info,
            mod_name
        )


    print(
        "CONFIG RESULT:",
        custom
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

    version_description = get_version_description(
       asset["name"],
       release_notes
    )

    release_description = get_release_description(
        asset["name"],
        release_notes
    )

    new_app = {
        
        "name":
            custom.get(
                "name",
                display_name
            ),

        "variantID":
             variant_id,

        "modName":
            format_mod_name(mod_name),

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
            release_description
            if release_description
            else custom.get(
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
            version_description
            if version_description
            else custom.get(
                "versionDescription",
                ""
            ),

        "downloadURL":
            asset["browser_download_url"],

        "size":
            asset["size"],

        "sha256":
            sha256
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

    repository = load_repository()

    # Rebuild repository from GitHub releases
    repository["apps"] = []

    config = load_config()

    releases = get_all_releases()

    for release in releases:

        notes = get_release_notes(
            release
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

    cleanup_deleted_releases(
    repository,
    releases
    )
    
    save_repository(
        repository
    )


    print(
        "FINAL CONFIG BEFORE SAVE:",
        config
    )


    save_config(
        config
    )


    print(
        "AshStore update completed"
    )


if __name__ == "__main__":

    main()
